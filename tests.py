import unittest
from client import Client
from server import Server
import threading
import time

host = '127.0.0.1'
port = 12346


class TestClientServer(unittest.TestCase):

    def remove_empty_data(self, data):
        """Removes empty data entries from the input list."""
        new_data = []
        for file in data:
            if isinstance(file, str) and len(file) > 0:
                new_data.append(file)
        return new_data

    def run_server(self, host, port):
        """Start the server to listen for incoming packets."""
        self.server = Server(host, port)
        self.server.handle_packet()

    def run_client(self, host, port, data):
        """Run the client to send the data over UDP."""
        self.client = Client(host, port)
        self.client.send_syn()  # Simulate handshake
        self.client.receive_ack()
        self.client.send_all_packets(data)  # Send data packets
        #self.client.send_fin_massage(host, port, packet_number=1, connection_id=1)
        #self.client.send_fin_massage(packet_number=1, connection_id=1)
        self.client.send_fin_massage(packet_number=1, connection_id=1, server_address=(host, port))
        self.client.close()

    def global_test(self, data):
        """Global test setup to run the server and client for different data sets."""
        data = self.remove_empty_data(data)
        send_data = [(i, data[i]) for i in range(len(data))]

        # Start the server in a separate thread
        server_thread = threading.Thread(target=self.run_server, args=(host, port))
        server_thread.start()

        time.sleep(1)  # Allow server to start before client sends data

        # Start the client in a separate thread to send data
        client_thread = threading.Thread(target=self.run_client, args=(host, port, send_data))
        client_thread.start()

        # Wait for both threads to finish
        server_thread.join()
        client_thread.join()

        # Compare received data with sent data
        received_data = self.server.files
        self.assertEqual(data, received_data)

    # Test different data conditions
    def test_short_data(self):
        data = ["hello"]
        self.global_test(data)

    def test_many_medium(self):
        data = ["a" * 1024 for _ in range(10)]  # 1 KB of data
        self.global_test(data)

    def test_long_data(self):
        data = ["a" * 1024 * 1024]  # 1 MB of data
        self.global_test(data)

    def test_empty_data(self):
        data = ["", "valid", "data" * 1024 * 1024, "", "valid again", "data" * 1024 * 1024]
        self.global_test(data)

    def test_none_string_data(self):
        data = [69 for _ in range(10)]  # non-string data
        with self.assertRaises(TypeError):
            self.global_test(data)

    def test_with_none_string_data(self):
        data = [69, "valid", "data" * 1024 * 1024, "", 69, "valid again"]
        with self.assertRaises(TypeError):
            self.global_test(data)

    def test_empty_data_only(self):
        data = ["" for _ in range(5)]
        self.global_test(data)

    def test_zero_files(self):
        data = []
        self.global_test(data)

    def test_many_small_streams(self):
        data = ["small" for _ in range(100)]
        self.global_test(data)


if __name__ == '__main__':
    unittest.main()

# import unittest
# from unittest.mock import patch
# from client import *
# from server import *
# import threading
# from server import Server  # Assuming this is the server class
#
# class MyTestCase(unittest.TestCase):
#     def setUp(self):
#         self.host = "localhost"
#         self.port = 12346
#         self.server = Server(self.host, self.port)  # Initialize the server
#         self.client = Client(self.host, self.port)
#
#     def run_server(self):
#         self.server.start()
#
#     def run_client_with_mocked_data(self, data):
#         with patch('client.Client.generate_random_files', return_value=['mocked_file.txt']):
#             with patch('builtins.open', unittest.mock.mock_open(read_data=data)):
#                 self.client.start(num_flows=1)
#
#     def run_both(self, data):
#         server_thread = threading.Thread(target=self.run_server)
#         server_thread.start()
#         time.sleep(1)  # Give the server time to start
#         client_thread = threading.Thread(target=self.run_client_with_mocked_data, args=(data,))
#         client_thread.start()
#         server_thread.join()
#         client_thread.join()
#
#     def test_short_data(self):
#         self.run_both("Hello World")
#         #assert self.server.files[0] == "Hello World"
#
#     def test_long_data(self):
#         self.run_both("A" * 1000000)
#         #assert self.server.files[0] == "A" * 1000000
#
#     def test_multiple_files(self):
#         self.run_both("A" * 1000)
#         self.run_both("B" * 1000)
#         #assert self.server.files[0] == "A" * 1000
#         #assert self.server.files[1] == "B" * 1000
#
#     def test_empty_data(self):
#         data = ""
#         self.run_both(data)
#
#
#
#
# if __name__ == '__main__':
#     unittest.main()
