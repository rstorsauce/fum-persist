import socket
import sys
import unittest
import time
import uuid
from fum import is_uuid
from fum import internal_fum_yield
from random import randint
import concurrent.futures

import asyncio

def build_yield_socket(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print('failed to create socket for yield on port: ' + str(port))
        exit(1)
    server_address = ('localhost', port)
    sock.bind(server_address)
    sock.listen(1)
    return sock

def socket_listener(host_port, numbytes):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('localhost', host_port)
    sock.bind(server_address)
    sock.listen(1)
    connection, client_address = sock.accept()
    data = connection.recv(numbytes)
    connection.close()
    sock.close()
    return data

class TestUUID(unittest.TestCase):

    def test_is_uuid_accepts_a_uuid(self):
        self.assertTrue(is_uuid("7587bce7-7c5c-49c9-94d0-cdb20fcbe5eb"))
        self.assertTrue(is_uuid(str(uuid.uuid4())))

    def test_is_uuid_rejects_bad_uuids(self):
        #reject when there's a strange value
        self.assertFalse(is_uuid("7587bce7-7c5c-49c9-94d0-cdb20fcbe5eq"))
        #reject when the length is wrong
        self.assertFalse(is_uuid("7587bce7-7c5c-49c9-94d0-cdb20fcbe5e"))
        #reject when hyphen is wrong.
        self.assertFalse(is_uuid("7587bce7a7c5c-49c9-94d0-cdb20fcbe5e"))

class TestFumYieldSuccess(unittest.TestCase):
    def test_no_blocking_when_no_port(self):
        res = internal_fum_yield(False, 0, None, '0', '', 0)
        self.assertTrue(0 == res)

    def test_node_responds_with_ok_when_ready(self):
        port = randint(10000,11000)
        sock = build_yield_socket(port)
        resp_port = randint(11000, 12000)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server_future = executor.submit(socket_listener, resp_port, 2)
            time.sleep(0.01)
            fyr = internal_fum_yield(False, port, sock, 0, 'localhost', resp_port)
            self.assertTrue(0 == fyr)
            self.assertTrue(b'ok' == server_future.result())
            sock.close()

if __name__ == '__main__':
    unittest.main()
