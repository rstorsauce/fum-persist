import socket
import sys
import os
import time
import logging

from uuid import UUID

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
        Fum.host_port = int(os.getenv('FUM_HOST_PORT', 0))
        # run-specific parameters
        Fum.current_uuid = ''
        #set up a global logger object
        Fum.logger = logging.getLogger(__name__)

        # build an actual socket that we'll save, but only
        # if node_port is a number.
        if Fum.node_port:
            try:
                Fum.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('localhost', Fum.node_port)
                Fum.sock.bind(server_address)
                Fum.sock.listen(1)
            except:
                Fum.info('failed to create socket for yield on port: ' + str(Fum.node_port))
                exit(1)

    #lets us mock exiting the tensorflow program, for tests.
    def exit(val):
        exit(val)

    def info(*args):
        Fum.logger.info(*args)
        print(*args, file=sys.stderr)
        sys.stderr.flush()

def is_uuid(uuid_string):
    try:
        val = UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False

def fum_node_yields__(fclass):
    fclass.info('signalling ok to', fclass.host_ip, 'at', fclass.host_port)
    resp_sock = 0
    try:
        #transiently create an output socket.
        resp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (fclass.host_ip, fclass.host_port)
        resp_sock.connect(server_address)
        resp_sock.sendall('ok'.encode())
        resp_sock.close()
        fclass.has_run = True
        return 0
    except:
        if resp_sock:
            resp_sock.close()
        #keep pinging the socket until we get a response.
        fclass.info('failed to send ok signal, going to bail.')
        fclass.exit(1)

def fum_node_waits__(fclass):
    fclass.info('waiting for job signal...')
    connection = False
    try:
        connection, client_address = fclass.sock.accept()
        #a uuid should be 36 bytes of data.
        data = connection.recv(36).decode('utf-8')
        if is_uuid(data):
            connection.sendall('ok'.encode())
            fclass.info('triggering job', data)
            fclass.current_uuid = data
            return data
        elif data == 'done':
            connection.sendall('done'.encode())
            fclass.info('terminate signal received')
            connection.close()
            fclass.sock.close()
            fclass.exit(0)
        else:
            fclass.info('strange data recieved')
            connection.close()
            fclass.sock.close()
            fclass.exit(1)
    except Exception as e:
        # just leave everything open since we're going to bail and the vm is
        # going to be reset anyways.
        fclass.info('error thrown: ', str(e))
        fclass.exit(1)
    finally:
        connection.close()

def fum_yield__(fclass):
    if fclass.node_port:
        fum_node_yields__(fclass)
        fum_node_waits__(fclass)
    else:
        if fclass.has_run:
            fclass.info('single run has been completed.')
            fclass.exit(0)
        else:
            fclass.info('persistent mode not detected, running singly')
            fclass.has_run = True
    return 0

def fum_yield():
    return fum_yield__(Fum)

