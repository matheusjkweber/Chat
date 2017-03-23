import curses
import curses.panel
import curses.ascii
import sys
import socket
import json
import time
import threading

# __enum = lambda *args, **kwargs: type('__enum', (), dict(zip(args, map(str, args)), **kwargs))


class Widget(object):
    __all_widgets = {}
    def __init__(self, **kwargs):
        self.lines = kwargs.get('lines')
        self.cols = kwargs.get('cols')
        self.name = kwargs.get('name')
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)

        if self.name and self.name in Widget.__all_widgets:
            raise TypeError('name \'%s\' is already defined.' % self.name)

        self.win = kwargs.get('win',
                              curses.newwin(self.lines,
                                            self.cols,
                                            self.y,
                                            self.x))
        self.panel = curses.panel.new_panel(self.win)

        for entry in dir(self.panel):
            attr = getattr(self.panel, entry)
            if callable(attr):
                setattr(self, entry, attr)

        Widget.__all_widgets.update({self.name: self})


    def on_focus(self):
        pass

    @staticmethod
    def get_widget(name):
        return Widget.__all_widgets.get(name)

class TextInput(Widget):

    def __init__(self, **kwargs):
        self.default_text = kwargs.get('default_text', None)
        self.label = kwargs.get('label', None)
        self.attr = kwargs.get('attr', curses.A_NORMAL)
        self.at_x = len(self.label) + 1 if self.label else 0
        kwargs['lines'] = 1
        super(TextInput, self).__init__(**kwargs)

        if self.label:
            self.win.addstr(0, 0, self.label)
        self.win.chgat(0, self.at_x, self.cols, self.attr)
        self.win.keypad(1)
        self.__buffer = []

    def on_focus(self):
        curses.curs_set(True)
        self.top()
        self.__on_focus()
        curses.curs_set(False)

    def __on_focus(self):
        win = self.win
        attr = self.attr
        _, max_x = win.getmaxyx()
        ch = 0
        while True:
            ch = win.getch()
            y, x = win.getyx()

            if max_x - x <= 4:
                buff = self.__buffer[-8:]
                win.insdelln(1)
                if self.label:
                    self.win.addstr(0, 0, self.label)
                self.win.chgat(0, self.at_x, self.cols, self.attr)
                win.addstr(y, self.at_x, ''.join(buff), attr)
                y, x = win.getyx()

            if ch in [ord('\n'), ord('\r'), ord('\t'), ord('\v')]:
                # curses.ungetch(ch)
                break
            elif ch == curses.KEY_BACKSPACE:
                if self.__buffer:
                    self.__buffer.pop()
                    if x == 4 + self.at_x and len(self.__buffer) > 4:
                        buff = self.__buffer[8 - (max_x - self.at_x):]
                        win.insdelln(1)
                        if self.label:
                            self.win.addstr(0, 0, self.label)
                        self.win.chgat(0, self.at_x, self.cols, self.attr)
                        win.addstr(y, self.at_x, ''.join(buff), attr)
                    else:
                        win.addch(y, x - 1, ' ', attr)
                        win.move(y, x - 1)
            elif curses.ascii.isprint(ch):
                self.__buffer.append(chr(ch))
                win.addch(y, x, chr(ch), attr)

            curses.panel.update_panels()
            curses.doupdate()

    def __str__(self):
        s = ''.join(self.__buffer)
        if self.label:
            self.win.addstr(0, 0, self.label)
        self.win.addstr(0, self.at_x, ' ' * (self.cols - self.at_x - 1), self.attr)
        self.win.move(0, self.at_x)
        self.win.keypad(1)
        self.__buffer = []
        return s

class ChatClient(object):

    class Commands(object):
        def __init__(self, self_):
            self.self_ = self_

        """ @connect <ip>:<port> nickname """
        def connect(self, args):
            message = None
            try:
                ip, port = args[1].split(':')
                self.self_.server_addr = (ip, int(port))
                self.self_.nickname = args[2]
                r = self.self_._login(self.self_.server_addr, args[2])
                if 200 <= r['code'] < 300:
                    self.self_.token = r.get('object')[1]
                    message = '[!] connected to {}:{}'.format(ip, port)
                else:
                    message = r['message']
            except socket.error as e:
                message = str(e)
            except Exception as e:
                # raise
                message = '[!] please use `@connect <server ip>:<server port> <nickname>\''
            return message

        def enter_room(self, args):
            self.__ensure_connected()
            self.self_.room = args[1]
            r = self.self_._enter_room(self.self_.server_addr, self.self_.token, args[1])
            success = 200 <= r.get('code') < 300
            message = '[!] {}'.format('OK' if success else r['message'])
            if success:
                self.self_._send_message_to_room(self.self_.server_addr, self.self_.token, self.self_.room, '~ {} entered the room'.format(self.self_.nickname))
                self.__listen(self.self_.room)
            return message

        def create_room(self, args):
            self.__ensure_connected()
            message = '[!] use @create-room <room name>'
            if len(args) > 1:
                r = self.self_._create_room(self.self_.server_addr, args[1])
                success = 200 <= r.get('code') < 300
                message = '[!] {}'.format('OK' if success else r['message'])

            return message

        def private(self, args):
            self.__ensure_connected()
            r = self.self_._send_private_message(self.self_.server_addr, self.self_.token, args[1], ' '.join(args[2:]))
            return ''


        def __listen(self, room):
            t = threading.Thread(target=self.self_._listener,
                                 args=(self.self_.server_addr, room))
            self.self_._keep_listener_alive = True
            t.daemon = True
            t.start()

        def people(self, args):
            self.__ensure_connected()
            message = '[!] use @people <room name>'
            if len(args) > 1:
                r = self.self_._get_users_room(self.self_.server_addr, args[1])
                success = 200 <= r.get('code') < 300
                message = 'room empty'
                if r['object']:
					message = 'in this room: {}'.format(reduce(lambda a, b: '{}, {}'.format(a, b), r['object']))
            return message

        def rooms(self, args):
            self.__ensure_connected()
            r = self.self_._get_rooms(self.self_.server_addr)
            success = 200 <= r.get('code') < 300
            message = 'no rooms created'
            if r['object']:
				message = 'rooms: {}'.format(reduce(lambda a, b: '{}, {}'.format(a, b), r['object']))
            return message

        def leave_room(self, args):
            self.__ensure_connected()
            self.self_._send_message_to_room(self.self_.server_addr,
                                       self.self_.token, self.self_.room,
                                       '~ {} left the room'.format(self.self_.nickname))
            r = self.self_._leave_room(self.self_.server_addr, self.self_.token, self.self_.room)
            success = 200 <= r.get('code') < 300
            message = '[-] you left.'
            self.self_.room = ''
            self.self_._keep_listener_alive = False
            return message

        def __ensure_connected(self):
            if not getattr(self.self_, 'server_addr', ''):
                raise Exception('[!] you have to be connected first.');

        def logout(self, args):
            self.__ensure_connected()
            r = self.self_._logout(self.self_.server_addr, self.self_.token)
            success = 200 <= r.get('code') < 300
            message = '[-] you are out ;)'
            return message

        def not_found(self, args):
            message = '[!] command `{}\' not found'.format(args[0])
            return message
        # def get_messages
        def kill(self, args):
            return 'kill'

    def __init__(self):
        self.stdscr = curses.initscr()
        self.max_y, self.max_x = self.stdscr.getmaxyx()

        self.whist = curses.newwin(self.max_y - 3, self.max_x, 0, 0)
        self.wconsole = curses.newwin(3, self.max_x, self.max_y - 3, 0)

        self.whist.box()
        self.wconsole.box()

        self.pconsole = curses.panel.new_panel(self.wconsole)
        self.phist = curses.panel.new_panel(self.whist)

        self.history = []
        self.history_lock = threading.Lock()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.start_color()
        curses.curs_set(False)
        console_y, console_x = self.wconsole.getbegyx()
        self.txt_input = TextInput(label='>', x=console_x+1, y=console_y+1, cols=self.max_x-2)
        curses.panel.update_panels()
        curses.doupdate()

    def update_messages(self, msg=None):
        with self.history_lock:
            if msg:
                self.history.append(msg)

            for i, line in enumerate(self.history[-self.max_y+5:], 1):
                self.whist.move(i, 2);
                self.whist.addstr('{}{}'.format(line, ' ' * (self.max_x - len(line) - 4)))

            curses.panel.update_panels()
            curses.doupdate()

    def loop(self):
        try:
            while True:
                self.txt_input.on_focus()
                s = str(self.txt_input)
                split = str.split(s)
                # log += str(split) + '\n'
                try:
                    s = self._execute(split)
                except Exception as e:
                    s = str(e)

                if 'kill' in s:
                    break
                # TODO: split long line into many lines
                self.update_messages(s)
        except:
            raise
        finally:
            curses.nocbreak()
            self.stdscr.keypad(0)
            curses.echo()
            curses.endwin()

    def _execute(self, args):
        cmd = ChatClient.Commands(self)
        if len(args) > 0 and args[0][0] == '@':
            c = args[0][1:]
            c = c.replace('-', '_')
            return getattr(cmd, c, cmd.not_found)([c] + args[1:])
        elif getattr(self, 'room', ''):
            m = ' '.join(args)
            # raise Exception(dir(self))
            r = self._send_message_to_room(self.server_addr, self.token, self.room, m)
            return '' if 200 <= r.get('code') < 300 else r.get('message')
        else:
            return ' '.join(args)

    def _listener(self, addr, room):
        count = 0
        count_p = 0
        while self._keep_listener_alive:
            r = self._get_messages_room(addr, room)
            messages = r['object']
            if len(messages) > count:
                for msg in messages[count:]:
                    m = 'from {}: {}'.format(msg[1], msg[2])
                    self.update_messages(m)
                count = len(messages)

            r = self._get_private_messages(addr, self.token)
            if 200 <= r['code'] < 300:
                messages = r['object']
                if len(messages) > count_p:
                    for msg in messages[count_p:]:
                        m = '[private] from {}: {}'.format(msg[1], msg[2])
                        self.update_messages(m)
                    count_p = len(messages)
            time.sleep(0.5)

    def _login(self, addr, nickname):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'login',
            'args': {
                'nickname': nickname,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _get_users_online(addr):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'get_users_online'
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _get_private_messages(self, addr, token):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'get_private_messages',
            'args': {
                'token': token
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _send_private_message(self, addr, token, nickname, message):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'send_private_message',
            'args': {
                'token': token,
                'nickname': nickname,
                'message': message
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)


    def _get_rooms(self, addr):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'get_rooms'
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _enter_room(self, addr, token, room_name):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'enter_room',
            'args': {
                'token': token,
                'room_name': room_name,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _create_room(self, addr, name):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'create_room',
            'args': {
                'name': name,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _get_users_room(self, addr, name):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'get_users_room',
            'args': {
                'name': name,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _get_messages_room(self, addr, name):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'get_messages_room',
            'args': {
                'name': name,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _send_message_to_room(self, addr, token, room_name, message):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'send_message_to_room',
            'args': {
                'token': token,
                'room_name': room_name,
                'message': message
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _leave_room(self, addr, token, room_name):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'leave_room',
            'args': {
                'token': token,
                'room_name': room_name
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

    def _logout(self, addr, token):
        s = socket.socket(); s.connect(addr)
        s.send(json.dumps({
            'execute':'logout',
            'args': {
                'token': token,
            }
        }))
        r = s.recv(4096); s.close()
        return json.loads(r)

if __name__ == '__main__':
    chat = ChatClient()
    chat.loop()
