import filecmp
import socket
import time

import client
from quic import *


class Server:

    def __init__(self, ip, port):
        self.server_address = (ip, port)                                        # Initialize the server with the IP and port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)
        self.bytes_per_stream = []
        self.packets_per_stream = []
        self.total_times = []
        self.total_bytes = 0
        self.total_packets = 0
        self.files = []
        self.total_time = 0
        self.avg_bytes_per_sec = []
        self.avg_packets_per_sec = []
        print(f"- Server listening on {self.server_address}...")

    def start(self):
        packet, client_address = self.server_socket.recvfrom(1024 * 1024 * 10)  # Receive data from the client (up to 10MB)
        deserialized_packet = Quic_packet.deserialize(packet)
        return deserialized_packet, client_address

    def handle_packet(self):
        start_time = time.time()
        while True:
            packet, client_address = self.start()

            # Check if the packet has the SYN flag set
            if packet.header.flags & 0b00000001:
                print("- - Received SYN packet")
                # Send a SYN-ACK response to acknowledge the SYN packet and establish a connection.
                self.send_syn_ack(client_address, packet.header.packet_number, packet.header.connection_id)

            # Check if the packet has the FIN flag set (indicating a connection termination request).
            if packet.header.flags & 0b00000100:
                print("- - - - Received FIN packet")
                # Send a FIN-ACK response to acknowledge the FIN packet and close the connection.
                self.send_fin_ack(client_address, packet.header.packet_number, packet.header.connection_id)
                # close the connection
                break

            # if it is a DATA packet
            if packet.header.flags & 0b00000010:
                # Process the received data packet.
                self.process_data_packet(packet, client_address)

        self.server_socket.close()
        self.print_statistics()

    def process_data_packet(self, packet, client_address):
        start_time = time.perf_counter()
        for frame in packet.frames:
            if frame.stream_id >= len(self.files):  # Check if the stream ID is within the expected range
                self.files += ["" for _ in range(frame.stream_id - len(self.files) + 1)]    # Add empty strings for new streams
                self.bytes_per_stream += [0 for _ in range(frame.stream_id - len(self.bytes_per_stream) + 1)]   # Add 0 bytes for new streams
                self.packets_per_stream += [0 for _ in range(frame.stream_id - len(self.packets_per_stream) + 1)]   # Add 0 packets for new streams
                self.total_times += [start_time for _ in range(frame.stream_id - len(self.total_times) + 1)]    # Add 0 time for new streams
            self.files[frame.stream_id] += frame.data   # Append the data to the corresponding stream
        finish_time = time.perf_counter()
        for frame in packet.frames: # Update the statistics for the received packet
            self.bytes_per_stream[frame.stream_id] += len(frame.data)   # Update the total bytes received for the stream
            self.packets_per_stream[frame.stream_id] += 1   # Update the total packets received for the stream
            self.total_bytes += len(frame.data) # Update the total bytes received
            self.total_times[frame.stream_id] += finish_time - start_time   # Update the total time for the stream
            self.avg_bytes_per_sec.append(self.bytes_per_stream[frame.stream_id] / (finish_time - start_time))  # Calculate the average data rate for the stream
            self.avg_packets_per_sec.append(self.packets_per_stream[frame.stream_id] / (finish_time - start_time))  # Calculate the average packet rate for the stream
        self.total_packets += 1  # Update the total packets received
        self.total_time += finish_time - start_time # Update the total time
        self.server_socket.sendto(packet.serialize(), client_address)   # Send an ACK packet to acknowledge the received data

    def print_statistics(self):
        """
        Print the statistics for each stream and overall data rates.
        """
        print("\n--------------------------------- Statistics ---------------------------------")
        print(f"\na.     Total Bytes Received For Each Stream:\n")  # a. Total Bytes Received For Each Stream
        for i in range(len(self.bytes_per_stream)):
            print(f"Stream {i}: {self.bytes_per_stream[i]} bytes")
        print("--------------------------------------------------------------------------------")
        print(f"\nb.     Total Packets Received For Each Stream:\n")    # b. Total Packets Received For Each Stream
        for i in range(len(self.packets_per_stream)):
            print(f"Stream {i}: {self.packets_per_stream[i]} packets")
        print("--------------------------------------------------------------------------------")
        print(f"\nc.     Data Rate By Bytes/Sec and Packet/Sec Per Stream:\n")  # c. Data Rate By Bytes/Sec and Packet/Sec Per Stream
        for i in range(len(self.bytes_per_stream)): # Calculate the average data rate for each stream
            stream_time = time.perf_counter() - self.total_times[i]
            avg_bytes_per_sec = self.bytes_per_stream[i] / stream_time if stream_time > 0 else 0
            avg_packets_per_sec = self.packets_per_stream[i] / stream_time if stream_time > 0 else 0
            print(f"Stream {i}: {avg_bytes_per_sec} bytes/sec, {avg_packets_per_sec} packets/sec")
        avg_total_bytes_per_sec = self.total_bytes / self.total_time if self.total_time > 0 else 0
        print("--------------------------------------------------------------------------------")
        print(f"\nd.     Overall Average Data Rate: {avg_total_bytes_per_sec} bytes/sec\n")     # d. Overall Average Data Rate
        avg_total_packets_per_sec = self.total_packets / self.total_time if self.total_time > 0 else 0
        print("--------------------------------------------------------------------------------")
        print(f"\ne.     Overall Average Packet Rate: {avg_total_packets_per_sec} packets/sec\n")   # e. Overall Average Packet Rate
        print("--------------------------------------------------------------------------------")
        print(f"\n-Received Files Comparison:\n")

        for i in range(len(self.files)):    # Save the received files to the output files
            output_file = f"output_{i}.txt"
            with open(output_file, "w") as f:
                f.write(self.files[i])

            # Compare with the original file
            original_file = f"random_file_{i}.txt"
            if self.compare_files(output_file, original_file):
                print(f"File {output_file} is identical to {original_file}.")
            else:
                print(f"File {output_file} is different from {original_file}.")
        return self.avg_bytes_per_sec, self.avg_packets_per_sec

    def compare_files(self, file1, file2):  # Compare two files to see if they are identical.
        return filecmp.cmp(file1, file2, shallow=False)

    def send_syn_ack(self, client_address, packet_number, connection_id):
        flags = 0b00000011
        frame = Frame(1, 0, 7, "SYN_ACK")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.server_socket.sendto(serialized_packet, client_address)
        print(f"- - - Sent SYN-ACK packet to {client_address}")

    def send_fin_ack(self, client_address, packet_number, connection_id):
        flags = 0b00000100
        frame = Frame(1, 0, 7, "FIN_ACK")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.server_socket.sendto(serialized_packet, client_address)
        print(f"- - - - - Sent FIN-ACK packet to {client_address}")


if __name__ == "__main__":
    server = Server("localhost", 12346)
    server.handle_packet()
