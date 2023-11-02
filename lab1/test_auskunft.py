"""
Simple client server unit test
"""

import logging
import threading
import unittest

import auskunft_protocol
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestAuskunftService(unittest.TestCase):
    """The test"""
    _server = auskunft_protocol.Server()  # create single server in class variable
    # define thread for running server
    _server_thread = threading.Thread(target=_server.serve)

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = auskunft_protocol.Client()  # create new client for each test

    def test_srv_getall(self):
        """Test get all phonebooks"""
        phonebooks = self.client.callall()
        self.assertIsInstance(phonebooks, list)

    def test_srv_getall_values(self):
        """Test get all phonebooks"""
        phonebooks = self.client.callall()
        phonevalues = [('John', '1234567890'),
                       ('Jane', '0987654321'),
                       ('Bob', '1122334455'),
                       ('Alice', '5566778899'),
                       ('Charlie', '2233445566'),
                       ('David', '3344556677'),
                       ('Eve', '4455667788'),
                       ('Frank', '5566778899'),
                       ('Grace', '6677889900'),
                       ('Heidi', '7788990011')]
        self.assertEqual(phonebooks, phonevalues)

    def test_srv_getnumber(self):
        """Test get a single phone number"""
        response = self.client.callnumber("Grace")
        self.assertEqual(response, ('Grace', '6677889900'))

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        # break out of server loop. pylint: disable=protected-access
        cls._server._serving = False
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
