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
    global log_file
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

#set up.
#if port:
#  eprint("setting up communication socket")
#  try:
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#  except:
#    eprint("fum_yield failed to create a socket")
#    exit(1)
#  server_address = (node_ip, port)
#  sock.bind(server_address)
#  sock.listen(1)

def internal_fum_yield(has_run, port, sock, node, resp_host, resp_port):
    if port:
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

#def fum_yield():
#    if port:
#        while True:
#            eprint("signalling ok to", resp_host, "at", resp_port)
#      try:
#        #transiently create an output socket.
#        resp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        server_address = (resp_host, resp_port)
#        resp_sock.connect(server_address)
#        resp_sock.sendall(bytes(node,"ascii"))
#        eprint("sent ok signal to host")
#        break
#      except:
#        #keep pinging the socket until we successfully get a response.
#        eprint("failed to send ok signal to host")
#        time.sleep(1)
#      finally:
#        resp_sock.close()
#
#    eprint("waiting for job signal...")
#    connection, client_address = sock.accept()
#    try:
#      #a uuid should be 36 bytes of data.
#      data = connection.recv(36).decode("utf-8")
#      if is_uuid(data):
#        connection.sendall(bytes("ok", "ascii"))
#        eprint("triggering job", data)
#        os.listdir("/input")
#      elif data == "no":
#        eprint("terminate signal received")
#        connection.close()
#        sock.close()
#        exit(0)
#      else:
#        eprint("strange data recieved")
#        connection.close()
#        sock.close()
#        exit(1)
#    finally:
#      connection.close()
#  else:
#    eprint("persistent mode not detected, running singly")
#    if has_run:
#      exit(0)
#    else:
#      has_run = True
#
