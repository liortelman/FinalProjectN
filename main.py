from server import *
from client import *

import threading
import matplotlib.pyplot as plt

# Statistics Arrays For The Graphs
average_bytes_statistics = []
average_packets_statistics = []

def run_server(host, port):
    server1 = Server(host, port)
    server1.handle_packet()
    avg_bytes, avg_packets = server1.print_statistics()
    average_bytes_statistics.append(sum(avg_bytes) / len(avg_bytes))
    average_packets_statistics.append(sum(avg_packets) / len(avg_packets))

def run_client(host, port, num_flows):
    client1 = Client(host, port)
    client1.start(num_flows)

def run_both(host, port, num_flows):
    for i in range(1, num_flows+1):
        print(f"\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Running test with {i} flows ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~\n")
        server_thread = threading.Thread(target=run_server, args=(host, port))
        server_thread.start()
        time.sleep(1)
        client_thread = threading.Thread(target=run_client(host, port, i), args=(host, port, num_flows))
        client_thread.start()
        server_thread.join()
        client_thread.join()

    plt.figure(figsize=(12, 6))
    plt.plot([i for i in range(1, num_flows + 1)], average_bytes_statistics, marker='o')
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Byte Rate')
    plt.title('Average Byte Rate As Function Of Streams NUmber')
    plt.savefig('bytes_statistics.png')
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot([i for i in range(1, num_flows + 1)], average_packets_statistics, marker='o')
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Packets per Second')
    plt.title('Average Packets per Second As Function Of Streams Number')
    plt.savefig('packets_statistics.png')
    plt.show()

    return average_bytes_statistics, average_packets_statistics

def save_stats_to_file(average_bytes_statistics, average_packets_statistics, filename):
    with open(filename, 'w') as f:
        for i in range(len(average_bytes_statistics)):
            f.write(f"Run {i + 1} With {i+1} Flows:\n")
            f.write(f"Average number of bytes per second: {[f'{byte_stat:.2f}' for byte_stat in average_bytes_statistics[i]]}\n")
            f.write(f"Average number of packets per second: {[f'{packet_stat:.2f}' for packet_stat in average_packets_statistics[i]]}\n")
            f.write("\n")


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12346
    runs = 10
    average_bytes_statistics, average_packets_statistics = run_both(host, port, runs)
    save_stats_to_file(average_bytes_statistics, average_packets_statistics, 'statistics.txt')

















#####################################################################################
################################### PREVIOUS CODE ###################################
# import random
# import time
# from client import Client
# from server import Server
# import threading
#
#
# def run_test(num_flows):
#     # Start server
#     server = Server("localhost", 12346)
#     threading.Thread(target=server.start).start()
#
#     # Wait for the server to start
#     time.sleep(1)
#
#     # Create and start client
#     client = Client("localhost", 12346)
#
#     # Create random flow sizes
#     flows = [random.randint(1000, 2000) for _ in range(num_flows)]
#     for flow_size in flows:
#         client.send_file("path/to/file", flow_size)  # Replace with actual method to send files
#
#     # Wait for all data to be sent
#     time.sleep(10)
#     client.close()
#     server.close()
#
#
# if __name__ == "__main__":
#     for num_flows in range(1, 11):
#         print(f"Running test with {num_flows} flows")
#         run_test(num_flows)
#         time.sleep(10)  # Delay between tests
