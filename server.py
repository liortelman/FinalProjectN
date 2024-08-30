import socket
import time

from quic import *


class Server:

    def __init__(self, ip, port):
        self.server_address = (ip, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)
        self.bytes_per_stream = {}
        self.packets_per_stream = {}
        self.start_times = {}
        self.total_bytes = 0
        self.total_packets = 0

    def start(self):
        print(f"Server listening on {self.server_address}...")
        while True:  # Keep listening for incoming packets
            packet, client_address = self.server_socket.recvfrom(1024 *1024 * 10)
            # Receive data from client in size of 1024*10 bytes
            # print(f"Received packet from {client_address}")
            deserialized_packet = Quic_packet.deserialize(packet)
            self.handle_packet(deserialized_packet, client_address)

    def handle_packet(self, packet, client_address):

        # Check if the packet has the SYN flag set
        if packet.header.flags & 0b00000001:
            print("Received SYN packet")
            # Send a SYN-ACK response to acknowledge the SYN packet and establish a connection.
            self.send_syn_ack(client_address, packet.header.packet_number, packet.header.connection_id)

        # Check if the packet has the FIN flag set (indicating a connection termination request).
        if packet.header.flags & 0b00000100:
            print("Received FIN packet")
            # Send a FIN-ACK response to acknowledge the FIN packet and close the connection.
            print_statistics()
            self.send_fin_ack(client_address, packet.header.packet_number, packet.header.connection_id)
            # close the connection
            self.close()

        # if it is a data packet
        if packet.header.flags & 0b00000010:
            # Process the received data packet.
            self.process_data_packet(packet)

    # def process_data_packet(self, packet):
    #     """
    #     need to extract statistic from the packet
    #      total number of bytes received  in each stream
    #     total number of packets received  in each stream
    #     average data(bytes per second) and packets(packets per second) in each stream
    #     total data : how many bytes received in a second in average
    #     total packets :how many packets received in average
    #
    #
    #     """

    def print_statistics(self):
        """
        Print the statistics for each stream and overall data rates.
        """

    def process_data_packet(self, packet):
        """
        Process a data packet to extract and update statistics for each stream.
        Tracks:
        - Total number of bytes received in each stream.
        - Total number of packets received in each stream.
        - Average data rate (bytes per second) and packet rate (packets per second) in each stream.
        - Total average data rate and packet rate across all streams.
        """
        current_time = time.time()

        for frame in packet.frames:
            stream_id = frame.stream_id

            # Initialize the stream statistics if it's the first time we receive data for this stream
            if stream_id not in self.bytes_per_stream:
                self.bytes_per_stream[stream_id] = 0
                self.packets_per_stream[stream_id] = 0
                self.start_times[stream_id] = current_time

            # Update statistics for this stream
            self.bytes_per_stream[stream_id] += len(frame.data)
            self.packets_per_stream[stream_id] += 1
            self.total_bytes += len(frame.data)
            self.total_packets += 1

        # Calculate averages
        total_time = current_time - min(self.start_times.values())

        # print("\n--- Stream Statistics ---")
        # for stream_id in self.bytes_per_stream:
        #     stream_time = current_time - self.start_times[stream_id]
        #     avg_bytes_per_sec = self.bytes_per_stream[stream_id] / stream_time if stream_time > 0 else 0
        #     avg_packets_per_sec = self.packets_per_stream[stream_id] / stream_time if stream_time > 0 else 0
        #     print(f"Stream {stream_id}:")
        #     print(f"  Total Bytes Received: {self.bytes_per_stream[stream_id]}")
        #     print(f"  Total Packets Received: {self.packets_per_stream[stream_id]}")
        #     print(f"  Average Bytes/Sec: {avg_bytes_per_sec}")
        #     print(f"  Average Packets/Sec: {avg_packets_per_sec}")

        avg_total_bytes_per_sec = self.total_bytes / total_time if total_time > 0 else 0
        avg_total_packets_per_sec = self.total_packets / total_time if total_time > 0 else 0
        print(f"\n--- Overall Statistics ---")
        print(f"Total Data Received: {self.total_bytes} bytes")                     # a

        print(f"Total Packets Received: {self.total_packets} packets")              # b

        print(f"Data Rate Per Stream:")                                             # c
        for (stream_id, bytes_received) in self.bytes_per_stream.items():
            stream_time = current_time - self.start_times[stream_id]
            avg_bytes_per_sec = bytes_received / stream_time if stream_time > 0 else 0
            print(f"  Stream {stream_id}: {avg_bytes_per_sec} bytes/sec")

        print(f"Data Rate Per Packet:")                                             # c
        for (stream_id, packets_received) in self.packets_per_stream.items():
            stream_time = current_time - self.start_times[stream_id]
            avg_packets_per_sec = packets_received / stream_time if stream_time > 0 else 0
            print(f"  Stream {stream_id}: {avg_packets_per_sec} packets/sec")

        print(f"Overall Average Packet Rate: {avg_total_packets_per_sec} packets/sec")      # d

        print(f"Overall Average Data Rate: {avg_total_bytes_per_sec} bytes/sec")            # d


    def send_syn_ack(self, client_address, packet_number, connection_id):
        flags = 0b00000011
        frame = Frame(1, 0, 7, "SYN_ACK")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.server_socket.sendto(serialized_packet, client_address)
        print(f"Sent SYN-ACK packet to {client_address}")

    def send_fin_ack(self, client_address, packet_number, connection_id):
        flags = 0b00000100
        frame = Frame(1, 0, 7, "FIN_ACK")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.server_socket.sendto(serialized_packet, client_address)
        print(f"Sent FIN-ACK packet to {client_address}")

    def close(self):
        self.server_socket.close()


if __name__ == "__main__":
    server = Server("localhost", 12346)
    server.start()

# import socket
# import threading
# from flow import Flow
#
#
# class QUICServer:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.flows = []
#
#     def start(self):
#         self.server_socket.bind((self.host, self.port))
#         self.server_socket.listen(5)
#         print("Server listening on port", self.port)
#
#         while True:
#             client_socket, addr = self.server_socket.accept()
#             print("Accepted connection from", addr)
#             threading.Thread(target=self.handle_client, args=(client_socket,)).start()
#
#     def handle_client(self, client_socket):
#         num_flows = int(client_socket.recv(1024).decode())
#         for _ in range(num_flows):
#             flow_id = client_socket.recv(1024).decode()
#             packet_size = int(client_socket.recv(1024).decode())
#             num_packets = int(client_socket.recv(1024).decode())
#             flow = Flow(flow_id, packet_size, num_packets)
#             self.flows.append(flow)
#             flow.send_flow(client_socket)
#         client_socket.close()
#
#
# if __name__ == "__main__":
#     server = QUICServer("localhost", 12345)
#     server.start()
