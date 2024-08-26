import random
import time
from client import Client
from server import Server
import threading


def run_test(num_flows):
    # Start server
    server = Server("localhost", 12346)
    threading.Thread(target=server.start).start()

    # Wait for the server to start
    time.sleep(1)

    # Create and start client
    client = Client("localhost", 12346)

    # Create random flow sizes
    flows = [random.randint(1000, 2000) for _ in range(num_flows)]
    for flow_size in flows:
        client.send_file("path/to/file", flow_size)  # Replace with actual method to send files

    # Wait for all data to be sent
    time.sleep(10)
    client.close()
    server.close()


if __name__ == "__main__":
    for num_flows in range(1, 11):
        print(f"Running test with {num_flows} flows")
        run_test(num_flows)
        time.sleep(10)  # Delay between tests
