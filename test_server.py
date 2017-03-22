from socket import socket
import json
import pprint

def wait_enter():
    # raw_input()
    pass

def log_response(r):
    pass


def lucas(addr):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'login',
        'args': {
            'nickname': 'lucas'
        }
    }))

    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    r = json.loads(r)
    token = r['object'][1]
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'create_room',
        'args': {
            'name': 'folia',
            # 'token': token
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'enter_room',
        'args': {
            'room_name': 'folia',
            'token': token
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'send_message_to_room',
        'args': {
            'room_name': 'folia',
            'token': token,
            'message': 'Oi tudo mundo?'
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    pedro(addr)
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'get_messages_room',
        'args': {
            'name': 'folia',
        }
    }))
    r = s.recv(4096); s.close()
    r = json.loads(r)

    print r



def pedro(addr):
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'login',
        'args': {
            'nickname': 'pedro'
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    r = json.loads(r)
    token = r['object'][1]
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'enter_room',
        'args': {
            'room_name': 'folia',
            'token': token
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()
    s = socket(); s.connect(addr)
    s.send(json.dumps({
        'execute':'send_message_to_room',
        'args': {
            'room_name': 'folia',
            'token': token,
            'message': 'Alguem??'
        }
    }))
    r = s.recv(4096); s.close();
    log_response(r)
    wait_enter()

if __name__ == '__main__':
    addr_raw = raw_input('server? ')
    ip, port = addr_raw.split(':')
    lucas((ip, int(port)))
