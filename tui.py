import curses
import curses.panel
import curses.ascii
import sys
import socket
import json

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
        def __init__(self, *args, **kwargs):
            pass

        """ @connect <ip>:<port> nickname """
        def connect(self, args):
            success = message = None
            try:
                ip, port = args[1].split(':')
                self.server_addr = (ip, int(port))
                s = socket.socket()
                s.connect(self.server_addr)
                s.send(json.dumps({
                    'execute':'login',
                    'args': {
                        'nickname': args[2],
                    }
                }))
                r = json.loads(s.recv(4096))
                s.close()
                self.token = r.get('object').get('token')
                success = 200 <= r.get('code') < 300
                message = '[!] connected to {}:{}'.format(ip, port)
            except socket.error as e:
                success = False
                message = str(e)
            except:
                success = False
                message = '[!] please use `@connect <server ip>:<server port> <nickname>\''

            return { 'success': success,
                     'message': message }

        def enter_room(self, args):
            success = True
            message = 'user entered the room'
            return { 'success': success,
                     'message': message }

        def private(self, args):
            success = True
            message = '[-] para {}: {}'.format(args[1], ' '.join(args[2:]))
            return { 'success': success,
                     'message': message }

        def not_found(self, args):
            success = True
            message = '   [!] command `{}\' not found'.format(args[0])
            return { 'success': success,
                     'message': message }
        def get_messages
        def kill(self, args):
            return {'success': True, 'kill': True}

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

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.start_color()
        curses.curs_set(False)
        console_y, console_x = self.wconsole.getbegyx()
        self.txt_input = TextInput(label='>', x=console_x+1, y=console_y+1, cols=self.max_x-2)
        curses.panel.update_panels()
        curses.doupdate()

    def loop(self):
        try:
            while True:
                self.txt_input.on_focus()
                s = str(self.txt_input)
                split = str.split(s)
                # log += str(split) + '\n'
                if len(split) > 0 and split[0][0] == '@':
                    r = self.__execute(split)
                    if 'kill' in r:
                        break
                    s = r['message']
                else:
                    s = '[+] para todos: {}'.format(s)
                # TODO: split long line into many lines
                self.history.append(s)
                for i, line in enumerate(self.history[-self.max_y+5:], 1):
                    self.whist.move(i, 2);
                    self.whist.addstr('{}{}'.format(line, ' ' * (self.max_x - len(line) - 4)))
                curses.panel.update_panels()
                curses.doupdate()
        except:
            raise
        finally:
            curses.nocbreak()
            self.stdscr.keypad(0)
            curses.echo()
            curses.endwin()

    def __execute(self, args):
        # print args
        c = args[0][1:]
        c = c.replace('-', '_')
        cmd = ChatClient.Commands()
        return getattr(cmd, c, cmd.not_found)([c] + args[1:])

if __name__ == '__main__':
    chat = ChatClient()
    chat.loop()
