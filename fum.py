import socket
import sys
import os
import time

# this is a convenient way to namespace key global variables outside of the main
# python namespace.  It's also mock-able so that we can run tests against fake Fums.
class Fum:
    #globals
    def setup():
        Fum.has_run = False
        # parameters for the node.
        Fum.node_port = int(os.getenv('FUM_NODE_PORT', 0))
        Fum.node_id = os.getenv('FUM_NODE_ID', '')
        Fum.node_ip = os.getenv('FUM_NODE_IP', '')
        # parameters for the host.
        Fum.host_ip = os.getenv('FUM_HOST_IP', '')
        Fum.host_port = int(os.getenv('FUM_PORT', 0))
        # run-specific parameters
        Fum.current_uuid = ""
        # build an actual socket that we'll save, but only
        # if node_port is a number.
        if Fum.node_port:
            try:
                Fum.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('localhost', Fum.node_port)
                Fum.sock.bind(server_address)
                Fum.sock.listen(1)
            except:
                Fum.eprint('failed to create socket for yield on port: ' + str(Fum.node_port))
                exit(1)
        # general parameters
        Fum.log = sys.stderr #open("/tmp/fumlog.txt", "a")

    #lets us mock exiting the tensorflow program, for tests.
    def exit(val):
        exit(val)

    def eprint(*args):
        print(*args, file=Fum.log)
        Fum.log.flush()

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

def fum_node_yields__(fclass):
    fclass.eprint('signalling ok to', fclass.host_ip, 'at', fclass.host_port)
    resp_sock = 0
    try:
        #transiently create an output socket.
        resp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (fclass.host_ip, fclass.host_port)
        resp_sock.connect(server_address)
        resp_sock.sendall('ok'.encode())
        resp_sock.close()
        return 0
    except:
        if resp_sock:
            resp_sock.close()
        #keep pinging the socket until we get a response.
        fclass.eprint('failed to send ok signal, going to bail.')
        fclass.exit(1)

def fum_node_waits__(fclass):
    fclass.eprint("waiting for job signal...")
    connection = False
    try:
        connection, client_address = fclass.sock.accept()
        #a uuid should be 36 bytes of data.
        data = connection.recv(36).decode("utf-8")
        if is_uuid(data):
            connection.sendall('ok'.encode())
            fclass.eprint("triggering job", data)
            fclass.current_uuid = data
            return data
        elif data == "done":
            connection.sendall('done'.encode())
            fclass.eprint("terminate signal received")
            connection.close()
            fclass.sock.close()
            fclass.exit(0)
        else:
            fclass.eprint("strange data recieved")
            connection.close()
            fclass.sock.close()
            fclass.exit(1)
    except:
        # just leave everything open since we're going to bail and the vm is
        # going to be reset anyways.
        fclass.exit(1)
    finally:
        connection.close()

def fum_yield__(fclass):
    if fclass.node_port:
        if fclass.has_setup:
            fum_node_waits__(fclass)
        fum_node_yields__(fclass)
    else:
        fclass.eprint("persistent mode not detected, running singly")
    return 0

def fum_yield():
    return fum_yield__(Fum)

#trigger the setup run to make sure all of our stateful stuff is going on.
Fum.setup()
