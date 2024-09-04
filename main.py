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
            # Fix: Directly format the float values
            f.write(f"Average number of bytes per second: {average_bytes_statistics[i]:.2f}\n")
            f.write(f"Average number of packets per second: {average_packets_statistics[i]:.2f}\n")
            f.write("\n")



if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12346
    runs = 10
    average_bytes_statistics, average_packets_statistics = run_both(host, port, runs)
    save_stats_to_file(average_bytes_statistics, average_packets_statistics, 'statistics.txt')

