from socket import socket
import json
import pprint
import threading

def wait_enter():
    # raw_input()
    pass

def log_response(r):
    pass

def lucas(addr):
    create_room(addr, 'teste1')

    print r

def login(addr, nickname):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'login',
        'args': {
            'nickname': nickname,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def get_users_online(addr):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_users_online'
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def get_private_messages(addr, token):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_private_messages',
        'args': {
            'token': token
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def send_private_message(addr, token, nickname, message):
    s = socket(); s.connect(addr)
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

def get_rooms(addr):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_rooms'
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def enter_room(addr, token, room_name):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'enter_room',
        'args': {
            'token': token,
            'room_name': room_name,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def get_users_room(addr, name):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_users_room',
        'args': {
            'name': name,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def get_messages_room(addr, name):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_messages_room',
        'args': {
            'name': name,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def send_message_to_room(addr, token, room_name, message):
    s = socket(); s.connect(addr)
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

def leave_room(addr, token, room_name):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'leave_room',
        'args': {
            'token': token,
            'room_name': room_name
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def logout(addr, token):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'logout',
        'args': {
            'token': token,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

def create_room(addr, name):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'create_room',
        'args': {
            'name': name,
        }
    }))
    r = s.recv(4096); s.close()
    return json.loads(r)

if __name__ == '__main__':
    addr_raw = raw_input('server? ')
    ip, port = addr_raw.split(':')
    addr = (ip, int(port))

    create_room(addr, 'room1')
    mauricio = login(addr, 'mauricio')['object'][1]
    pedro = login(addr, 'pedro')['object'][1]
    matheus = login(addr, 'matheus')['object'][1]

    enter_room(addr, mauricio, 'room1')
    enter_room(addr, pedro, 'room1')
    enter_room(addr, matheus, 'room1')

    send_message_to_room(addr, mauricio, 'room1', 'Ola povo. blz?')
    send_message_to_room(addr, matheus, 'room1', 'Certinho e tu ?')

    get_messages_room(addr, 'room1')
