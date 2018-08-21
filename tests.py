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

def send_data(port, data, resp_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', port)
    sock.connect(server_address)
    sock.sendall(data.encode())
    if resp_size:
        resp_data = sock.recv(resp_size)
        sock.close()
        return resp_data
    sock.close()

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

class TestEmptyFum(unittest.TestCase):

    class EmptyFum:
        node_port = 0
        def eprint(*args):
            pass

    def test_no_blocking_when_no_port(self):
        res = fum_yield__(TestEmptyFum.EmptyFum)
        self.assertTrue(0 == res)


class TestFumYield(unittest.TestCase):

    class FumForYieldTest:
        host_port = 0
        host_ip = 'localhost'
        exited = False
        def eprint(*args):
            pass
        def exit(_):
            TestFumYield.FumForYieldTest.exited = True

    def test_yield_responds_with_ok_when_ready(self):
        host_port = randint(11000, 11999)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server_future = executor.submit(socket_listener, host_port, 2)
            TestFumYield.FumForYieldTest.host_port = host_port
            time.sleep(0.01)
            res = fum_node_yields__(TestFumYield.FumForYieldTest)
            self.assertTrue(0 == res)
            self.assertTrue(b'ok' == server_future.result())

    def test_connection_failure_bails_out(self):
        # create a port destination that doesn't actually have a port created
        # behind it.  This should yield a TCP/IP connection error.
        host_port = randint(11000, 11999)
        TestFumYield.FumForYieldTest.host_port = host_port
        fum_node_yields__(TestFumYield.FumForYieldTest)
        self.assertTrue(TestFumYield.FumForYieldTest.exited)

class TestFumWait(unittest.TestCase):

    class FumForWaitTest:
        exitval = -1
        def eprint(*args):
            pass
        def exit(val):
            TestFumWait.FumForWaitTest.exitval = val

    def test_wait_responds_with_ok_when_delivered_uuid(self):
        node_port = randint(12000, 12999)
        TestFumWait.FumForWaitTest.sock = build_socket(node_port)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            node_future = executor.submit(fum_node_waits__, TestFumWait.FumForWaitTest)
            time.sleep(0.01)
            rand_uuid = str(uuid.uuid4())
            host_res = send_data(node_port, rand_uuid, 2)
            self.assertTrue(b'ok' == host_res)
            self.assertTrue(rand_uuid == node_future.result())
        TestFumWait.FumForWaitTest.sock.close()

    def test_wait_responds_with_done_when_sent_done(self):
        node_port = randint(12000, 12999)
        TestFumWait.FumForWaitTest.sock = build_socket(node_port)
        TestFumWait.FumForWaitTest.exitval = -1
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            node_future = executor.submit(fum_node_waits__, TestFumWait.FumForWaitTest)
            time.sleep(0.01)
            host_res = send_data(node_port, 'done', 4)
            self.assertTrue(b'done' == host_res)
            self.assertTrue(0 == TestFumWait.FumForWaitTest.exitval)
        TestFumWait.FumForWaitTest.sock.close()

    def test_wait_bails_when_sent_strange_data(self):
        node_port = randint(12000, 12999)
        TestFumWait.FumForWaitTest.sock = build_socket(node_port)
        TestFumWait.FumForWaitTest.exitval = -1
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            node_future = executor.submit(fum_node_waits__, TestFumWait.FumForWaitTest)
            time.sleep(0.01)
            host_res = send_data(node_port, 'XXXX', 0)
            time.sleep(0.01)
            self.assertTrue(1 == TestFumWait.FumForWaitTest.exitval)
        TestFumWait.FumForWaitTest.sock.close()

    def test_wait_bails_on_communication_error(self):
        node_port = randint(12000, 12999)
        #don't build the port.
        TestFumWait.FumForWaitTest.exitval = -1
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            node_future = executor.submit(fum_node_waits__, TestFumWait.FumForWaitTest)
            time.sleep(0.01)
            self.assertTrue(1 == TestFumWait.FumForWaitTest.exitval)

if __name__ == '__main__':
    unittest.main()
