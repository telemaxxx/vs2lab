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
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

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

    def test_srv_getnumber(self):
        """Test get a single phone number"""
        response = self.client.callnumber("Grace")
        self.assertEqual(response, ('Grace', '6677889900'))

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
