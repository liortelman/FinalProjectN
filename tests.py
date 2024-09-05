import unittest
from client import Client
from server import Server
import threading
import time

host = '127.0.0.1'
port = 12346


class TestClientServer(unittest.TestCase):
    def run_server(self, host, port):
        """Start the server to listen for incoming packets."""
        self.server = Server(host, port)
        self.server.handle_packet()

    def run_client(self, host, port, data):
        """Run the client to send the data over UDP."""
        self.client = Client(host, port)
        self.client.send_syn()  # Simulate handshake
        self.client.receive_ack()   # Receive the ACK packet
        self.client.send_all_packets(data)  # Send data packets
        time.sleep(0.0005)
        self.client.send_fin_massage(packet_number=1, connection_id=1, server_address=(host, port))
        self.client.close()

    def run_both_for_testing(self, data):
        input = data.copy()
        # Start the server in a separate thread
        server_thread = threading.Thread(target=self.run_server, args=(host, port))
        server_thread.start()

        time.sleep(1)  # Allow server to start before client sends data

        # Start the client in a separate thread to send data
        client_thread = threading.Thread(target=self.run_client, args=(host, port, data))
        client_thread.start()

        # Wait for both threads to finish
        server_thread.join()
        client_thread.join()

        # Compare received data with sent data
        received_data = self.server.files
        print ("Received data: ", received_data)
        print("Sent data: ", input)
        self.assertEqual(input, received_data)

    # Test different data conditions
    def test_short_data(self):
        data = ["short"]  # Single short file
        self.run_both_for_testing(data)

    def test_set_short(self):
        data = ["short" for _ in range(10)]
        self.run_both_for_testing(data)

    def test_medium_data(self):
        data = ["a" * 1024]
        self.run_both_for_testing(data)

    def test_set_medium(self):
        data = ["a" * 1024 for _ in range(10)]  # Set of files composed of 1 KB of a's
        self.run_both_for_testing(data)

    def test_long_data(self):
        data = ["a" * 1024 * 1024]  # Set of files A file composed of 1 MB of a's
        self.run_both_for_testing(data)

    def test_set_long(self):
        data = ["a" * 1024 * 1024 for _ in range(10)]
        self.run_both_for_testing(data)

    def test_non_string_data(self):
        data = [123 for _ in range(10)]  # non-string data
        with self.assertRaises(TypeError):
            Client.send_all_packets(data)

    def test_empty_file(self):
        data = [""]
        self.run_both_for_testing(data)

    def test_set_empty_files(self):
        data = ["" for _ in range(10)]  # Empty files
        self.run_both_for_testing(data)

    def test_no_data(self):
        data = []
        self.run_both_for_testing(data)


if __name__ == '__main__':
    unittest.main()
