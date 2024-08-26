# file for implementation of QUIC packet
# serilization and deserialization functions.
# each quic packet has a header and a payload
# header is 9 bytes
# 1 byte for 4 flags(ack, syn, fin,data)
# 4 bytes for packet number
# 4 bytes for connection id

# paylode contains frames
# each frame stream contains (id, offset, data length, data)


# 1. QUIC Packet Structure
# Header (9 bytes total)
# Flags (1 byte): Four flags (ACK, SYN, FIN, DATA) packed into a single byte.
# Packet Number (4 bytes): A unique identifier for the packet within the connection.
# Connection ID (4 bytes): Identifies the connection to which this packet belongs.

# Payload
# Contains multiple frames, each of which carries a part of a stream of data. A frame is defined by:
# Stream ID (2 bytes): Identifies the stream within the connection.
# Offset (variable size): Indicates where this frame’s data fits into the stream.
# Data Length (variable size): Specifies the length of the data in this frame.
# Data (variable size): The actual data being transmitted.


# 2. Serialization
# The serialize_packet function takes a QUICPacket object and returns a byte string.
# The packet’s header is serialized first, followed by the payload frames.
# Each frame is serialized by concatenating the stream ID, offset, data length, and data.
# The stream ID is serialized as a 2-byte integer
# the offset and data length are serialized as variable-length integers.
# The data is serialized as-is.

# 3. Deserialization
# The deserialize_packet function takes a byte string and returns a QUICPacket object.
# The header is deserialized first, followed by the payload frames.
# The header is unpacked into the flags, packet number, and connection ID.
# The payload is parsed by reading frames until the end of the byte string.
# Each frame is parsed by reading the stream ID, offset, data length, and data.
# The stream ID is read as a 2-byte integer, and the offset and data length are read as variable-length integers.
# The data is read as-is.

# 4. Variable-Length Integers
# Variable-length integers are used to encode the offset and data length in the frame structure.
# The serialize_varint and deserialize_varint functions are used to encode and decode these integers.
# The integer is split into 7-bit chunks, with the 8th bit indicating whether more bytes are present.
# The chunks are serialized in little-endian order, with the 8th bit set for all but the last chunk.
# The chunks are deserialized by reading the 7 bits and checking the 8th bit to determine if more bytes are present.
# The integer is reconstructed by shifting the 7-bit chunks into place and adding them together.

import struct


class Quic_packet:
    # +------------------------+
    # |      connection ID     |
    # |------------------------|
    # |     packet number      |
    # |------------------------|
    # | syn | ack | data | fin |                     +-------------+
    # |------------------------|   ->each frame =    |  stream id  |
    # |                        |                     |-------------|
    # |------------------------|                     |   offset    |
    # |          ...           |                     |-------------|
    # |------------------------|                     | data length |
    # |        frame 1         |                     |-------------|
    # |------------------------|                     |    data     |
    # |          ...           |                     +-------------+
    # |------------------------|
    # |        frame n         |
    # |------------------------+

    def __init__(self, flags, packet_number, connection_id, frames):
        self.header = Header(connection_id, packet_number, flags)
        self.frames = frames

    def serialize(self):
        # Serialize header
        serialized_packet = self.header.serialize()
        # Serialize frames
        for frame in self.frames:
            serialized_packet += frame.serialize()

        return serialized_packet

    @staticmethod
    def deserialize(data):
        # Deserialize header - length of header is 9 bytes
        deserialized_header = Header.deserialize(data[:9])
        data = data[9:]

        # Deserialize frames each frame (contains stream_id, offset, data_length, data)
        # check what is the length of each frame
        # frame_length = 18 + data_length
        frames = []
        while data:
            # 18 bytes for stream_id, offset, data_length + data_length
            frame_size = 18 + struct.unpack("!Q", data[10:18])[0]
            frame = Frame.deserialize(data[:frame_size])
            frames.append(frame)
            data = data[frame_size:]

        return Quic_packet(deserialized_header.flags, deserialized_header.packet_number, deserialized_header.connection_id , frames)


class Header:
    # +------------------------+
    # |      connection ID     |
    # |------------------------|
    # |     packet number      |
    # |------------------------|
    # | syn | ack | data | fin |
    # +------------------------+
    def __init__(self, connection_id, packet_number, flags):
        self.connection_id = connection_id
        self.packet_number = packet_number
        self.flags = flags

    def serialize(self):
        # Pack connection_id, packet_number, and flags into 9 bytes with network byte order
        return struct.pack("!IIB", self.connection_id, self.packet_number, self.flags)

    @staticmethod
    def deserialize(data):
        # Unpack 9 bytes into connection_id, packet_number, and flags with network byte order
        connection_id, packet_number, flags = struct.unpack("!IIB", data)
        return Header(connection_id, packet_number, flags)


class Frame:
    # +-------------+
    # |  stream id  |
    # |-------------|
    # |   offset    |
    # |-------------|
    # | data length |
    # |-------------|
    # |    data     |
    # +-------------+
    def __init__(self, stream_id, offset, data_length, data):
        self.stream_id = stream_id
        self.offset = offset
        self.data_length = data_length
        self.data = data

    def serialize(self):
        # Serialize stream_id as 2-byte integer, offset as 8 bytes , data_length 8 bytes , data as-is
        return struct.pack("!HQQ", self.stream_id, self.offset, self.data_length) + self.data.encode('utf-8')
        # TO DO: check if encode is correct

        serialized_frame += self.data.encode('utf-8') ## Append the frame's data (self.data), encoded in UTF-8, to the serialized frame string (serialized_frame)
        return serialized_frame ## Return the serialized frame string (serialized_frame) containing the UTF-8 encoded data

    @staticmethod
    def deserialize(data):
        # Deserialize 18 bytes into stream_id, offset, data_length, and data
        stream_id, offset, data_length = struct.unpack("!HQQ", data[:18])
        data = data[18:]
        return Frame(stream_id, offset, data_length, data.decode('utf-8'))