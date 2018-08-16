import socket
import sys
import os
import time

#globals
port = int(os.getenv('FUM_PORT_NODE', 0))
node = os.getenv('FUM_NODE', '')
node_ip = os.getenv('FUM_NODE_IP', '')
has_run = False
resp_host = os.getenv('FUM_HOST', '')
resp_port = int(os.getenv('FUM_PORT', 0))

log_file = sys.stderr #open("/tmp/fumlog.txt", "a")

def eprint(*args):
    print(*args, file=log_file)
    log_file.flush()

def is_uuid(uuid):
    if len(uuid) != 36:
        return False
    for idx in range(len(uuid)):
        if idx in [8, 13, 18, 23]:
            if uuid[idx] != '-':
                return False
        else:
            if not (uuid[idx] in '0123456789abcdef'):
                return False
    return True

def fum_node_yields__(resp_host, resp_port):
    while True:
        eprint('signalling ok to', resp_host, 'at', resp_port)
        try:
            #transiently create an output socket.
            resp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (resp_host, resp_port)
            resp_sock.connect(server_address)
            resp_sock.sendall('ok'.encode())
            break
        except:
            #keep pinging the socket until we get a response.
            eprint('failed to send ok signal, going to retry.')
            time.sleep(1)
        finally:
            resp_sock.close()
    return 0

def fum_node_waits__(sock):
    eprint("waiting for job signal...")
    connection, client_address = sock.accept()
    try:
        #a uuid should be 36 bytes of data.
        data = connection.recv(36).decode("utf-8")
        if is_uuid(data):
            connection.sendall('ok'.encode())
            eprint("triggering job", data)
            return data
        elif data == "done":
            eprint("terminate signal received")
            connection.close()
            sock.close()
            exit(0)
        else:
            eprint("strange data recieved")
            connection.close()
            sock.close()
            exit(1)
    finally:
        connection.close()

def fum_yield__(has_setup, socket, resp_host, resp_port):
    if resp_port:
        if has_setup:
            fum_node_waits__(socket)
        fum_node_yields__(resp_host, resp_port)
    else:
        eprint("persistent mode not detected, running singly")
    return 0
