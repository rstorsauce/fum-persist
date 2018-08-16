import socket
import sys
import unittest
import time
import uuid
from fum import *
from random import randint
import concurrent.futures

import asyncio

def build_socket(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print('failed to create socket for yield on port: ' + str(port))
        exit(1)
    server_address = ('localhost', port)
    sock.bind(server_address)
    sock.listen(1)
    return sock

def send_uuid(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', port)
    sock.connect(server_address)
    rand_uuid = str(uuid.uuid4())
    sock.sendall(rand_uuid.encode())
    data = sock.recv(2)
    sock.close()
    return data, rand_uuid

def socket_listener(host_port, numbytes):
    sock = build_socket(host_port)
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
        res = fum_yield__(False, None, '', 0)
        self.assertTrue(0 == res)

    def test_yield_responds_with_ok_when_ready(self):
        resp_port = randint(11000, 11999)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server_future = executor.submit(socket_listener, resp_port, 2)
            time.sleep(0.01)
            fyr = fum_node_yields__('localhost', resp_port)
            self.assertTrue(0 == fyr)
            self.assertTrue(b'ok' == server_future.result())

    def test_wait_responds_with_ok_when_delivered(self):
        node_port = randint(12000, 12999)
        sock = build_socket(node_port)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            node_future = executor.submit(fum_node_waits__, sock)
            time.sleep(0.01)
            host_res, rand_uuid = send_uuid(node_port)
            self.assertTrue(b'ok' == host_res)
            self.assertTrue(rand_uuid == node_future.result())
        sock.close()


if __name__ == '__main__':
    unittest.main()
