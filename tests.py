import unittest
from unittest.mock import patch
from client import *
from server import *
import threading
from server import Server  # Assuming this is the server class

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 12346
        self.server = Server(self.host, self.port)  # Initialize the server
        self.client = Client(self.host, self.port)

    def run_server(self):
        self.server.start()

    def run_client_with_mocked_data(self, data):
        with patch('client.Client.generate_random_files', return_value=['mocked_file.txt']):
            with patch('builtins.open', unittest.mock.mock_open(read_data=data)):
                self.client.start(num_flows=1)

    def run_both(self, data):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        time.sleep(1)  # Give the server time to start
        client_thread = threading.Thread(target=self.run_client_with_mocked_data, args=(data,))
        client_thread.start()
        server_thread.join()
        client_thread.join()

    def test_short_data(self):
        self.run_both("Hello World")
        #assert self.server.files[0] == "Hello World"

    def test_long_data(self):
        self.run_both("A" * 1000000)
        #assert self.server.files[0] == "A" * 1000000

    def test_multiple_files(self):
        self.run_both("A" * 1000)
        self.run_both("B" * 1000)
        #assert self.server.files[0] == "A" * 1000
        #assert self.server.files[1] == "B" * 1000

    def test_empty_data(self):
        data = ""
        self.run_both(data)




if __name__ == '__main__':
    unittest.main()
