import socket
from quic import *


class Server:

    def __init__(self, ip, port):
        self.server_address = (ip, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)

    def start(self):
        print(f"Server listening on {self.server_address}...")
        while True: # Keep listening for incoming packets
            data, client_address = self.server_socket.recvfrom(1024)
            print(f"Received packet from {client_address}")
            packet = Quic_packet.deserialize(data)
            print(
                f"Received packet with packet number {packet.header.packet_number} and connection ID {packet.header.connection_id} and data {packet.frames[0].data} and flags {packet.header.flags}")

            # If the packet has the SYN flag set, send a  SYN ACK
            if packet.header.flags & 0b00000001:
                print("Received SYN packet")
                self.send_syn_ack(client_address, packet.header.packet_number, packet.header.connection_id)

    def handle_packet(self, packet, client_address):
        ## Print packet details: Shows the packet number, connection ID, and flags from the received packet.
        print(f"Received packet with packet number {packet.header.packet_number}, "
              f"connection ID {packet.header.connection_id}, and flags {packet.header.flags}")

        ## Check if the packet has the SYN flag set (indicating a new connection request).
        if packet.header.flags & 0b00000001:
            print("Received SYN packet")  ## Inform that a SYN packet was received.
            ## Send a SYN-ACK response to acknowledge the SYN packet and establish a connection.
            self.send_syn_ack(client_address, packet.header.packet_number, packet.header.connection_id)

        ## Iterate through each frame in the packet for further processing.
        for frame in packet.frames:
            flow_id = frame.flow_id  ## Extract the flow ID from the frame.
            offset = frame.offset  ## Extract the offset from the frame.
            length = frame.length  ## Extract the length of the data in the frame.
            data = frame.data  ## Extract the data from the frame.

            ## Print details of the received frame: Shows flow ID, offset, length, and the actual data.
            print(f"Received frame for flow {flow_id}: offset {offset}, length {length}, data {data}")

            ## Process the received frame data (e.g., save to a file, buffer it, etc.).
            ## You need to implement the actual data handling logic in the process_frame method.
            self.process_frame(flow_id, offset, data)

    def send_syn_ack(self, client_address, packet_number, connection_id):
        flags = 0b00000011
        frame = Frame(1, 0, 7, "SYN_ACK")
        packet = Quic_packet(flags, packet_number, connection_id, [frame])
        serialized_packet = packet.serialize()
        self.server_socket.sendto(serialized_packet, client_address)
        print(f"Sent SYN-ACK packet to {client_address}")

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