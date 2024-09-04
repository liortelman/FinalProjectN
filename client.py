# build an udp socket implementing the quic multy flow/streams
# creating udp socket and sending 10 files
# each file will be 2 mb and will be generated by random data
# each file will be sent in a different stream
# The client will now send each file over a stream with a consistent chunk size per stream.
# The chunk size will be randomized between 1000 and 2000 bytes.
import os

# each packet contains frames from diffrent streams,where each stream have the same size of the quic packet
from quic import *
import socket
import threading
import time
import random
import string


class Client:
    def __init__(self, ip, port):  # Initialize the client with the server's IP and port
        self.server_address = (ip, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.chunk_size = random.randint(1000, 2000)  # Consistent chunk size for each packet
        self.stream_id_counter = 0


    def generate_random_files(self, num_flows):
        """
                Generate random binary files for the given number of flows (streams).
                Each file is 2MB in size.

                :param num_flows: Number of files (streams) to generate.
                :return: List of generated file paths.
                """
        files = []
        file_size = 2 * 1024 * 1024  # 2MB in bytes
        for i in range(num_flows):
            file_name = f'random_file_{i}.txt'
            with open(file_name, 'w') as f:
                # Generate random bytes of size 2MB (2 * 1024 * 1024 bytes)
                random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=file_size))
                f.write(random_data)
            files.append(file_name)
        return files

    def create_packet(self, packet_number, data, offsets, percentage=60):

        flags = 0b00000010  # Data flag indicating this packet contains data frames
        total_streams = len(data)
        frame_percentage = round(total_streams * (percentage / 100))
        frames_num = min(frame_percentage, total_streams)
        frame_size = round(self.chunk_size / frames_num)
        frames = []
        streams_to_remove = []

        # Iterate over streams in sequential order (0 to len(data)-1)
        for stream_id in range(total_streams):
            if len(frames) >= frames_num:
                break

            if stream_id >= len(data):
                continue

            stream_data = data[stream_id]
            chunk_data = stream_data[offsets[stream_id]:offsets[stream_id] + frame_size]
            frames.append(Frame(stream_id + self.stream_id_counter, offsets[stream_id], len(chunk_data), chunk_data))
            offsets[stream_id] += len(chunk_data)

            # Check if the entire stream has been sent
            if offsets[stream_id] >= len(stream_data):
                streams_to_remove.append(stream_id)
                print(f"File corresponding to stream {stream_id + self.stream_id_counter} fully sent with size {len(stream_data)} bytes")

        # Remove fully sent streams
        for stream_id in sorted(streams_to_remove, reverse=True):
            if stream_id < len(data):
                data.pop(stream_id)
                self.stream_id_counter += 1
                offsets.pop(stream_id)
        packet = Quic_packet(flags=flags, packet_number=packet_number, connection_id=1, frames=frames)
        return packet, data, offsets

    def send_packet(self, packet):
        """
        Send the given packet to the server.

        :param packet: The QUIC packet to be sent.
        """
        serialized_packet = packet.serialize()
        self.client_socket.sendto(serialized_packet, self.server_address)
        # print(f"Sent packet to {self.server_address} with packet number {packet.header.packet_number}")

    def send_all_packets(self, data):
        packet_number = 1
        offsets = [0 for _ in range(len(data))]
        fin_sent = False

        while data:
            packet, data, offsets = self.create_packet(packet_number, data, offsets)
            self.send_packet(packet)
            time.sleep(0.0005)
            packet_number += 1

        if not fin_sent:
            self.send_fin_massage(self.server_address, packet_number, 1)
            fin_sent = True

        print("All data has been sent")

    def send_syn(self):
        """
               Send a SYN packet to initiate the connection with the server.
         """
        # Set up a QUIC packet with the SYN flag set (assuming SYN is the first bit)
        flags = 0b00000001  # SYN flag
        packet_number = 1
        connection_id = 1
        # frame will contain the word "SYN"
        frame = Frame(1, 0, 3, "SYN")

        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.client_socket.sendto(serialized_packet, self.server_address)
        print(f"Sent SYN packet to {self.server_address} with flags {flags}")

    def receive_ack(self):
        """
                Receive an ACK packet from the server to confirm the connection.
         """
        data, server_address = self.client_socket.recvfrom(1024)
        print(f"Received packet from {server_address}")
        packet = Quic_packet.deserialize(data)

        if packet.header.flags & 0b00000011:
            print(f"Received packet with packet number {packet.header.packet_number} and connection ID {packet.header.connection_id} and data {packet.frames[0].data}")

    def close(self):
        """
                Close the client socket connection.
         """
        self.client_socket.close()

    def send_fin_massage(self, server_address, packet_number, connection_id):
        flags = 0b00000100
        frame = Frame(1, 0, 3, "FIN")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.client_socket.sendto(serialized_packet, server_address)
        print(f"Sent FIN packet to {server_address}")


    def start(self, num_flows):
        client = Client("localhost", 12346)
        client.send_syn()
        client.receive_ack()
        num_files = num_flows  # Number of files
        files = client.generate_random_files(num_files)  # Generate X random files

        # Load the content of the generated files into memory
        data = [open(file, 'r').read() for file in files]
        # data = [(file_id, file_data) for file_id, file_data in files]

        client.send_all_packets(data)  # Send packets until all files are fully transmitted
        time.sleep(0.0005)
        client.close()  # Close the connection


############### IM DOING FUNCTION FROM THE MAIN TO START THE CLIENT ################
# if __name__ == "__main__":
#     client = Client("localhost", 12346)
#     client.send_syn()
#     client.receive_ack()
#     num_files = 10  # Number of files
#     files = client.generate_random_files(num_files)  # Generate 10 random files
#
#     # Load the content of the generated files into memory
#     data = [open(file, 'r').read() for file in files]
#     # data = [(file_id, file_data) for file_id, file_data in files]
#
#     client.send_all_packets(data)  # Send packets until all files are fully transmitted
#     time.sleep(0.0005)
#     client.close()  # Close the connection
