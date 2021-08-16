from __future__ import annotations
import struct, array

# B unsigned char (8 bits) 1 byte
# H unsigned short (16 bits) 2 bytes
# s char[] n bytes

class Packet:
    _FORMAT: str = "BBHHH6s"

    def __init__(self, data: bytes = None, message_type: int = None, code: int = None, checksum: int = 0x000, bytes: bytes = None) -> None:
        if bytes:
            self.bytes = bytes
            decoded = self.human_readable
            
            self.message_type = decoded[0]
            self.code = decoded[1]
            self.checksum = decoded[2]
            self.id = decoded[3]
            self.sequence_number = decoded[4]
            self.data = decoded[5]
        else:
            self.data = data
            self.message_type = message_type
            self.code = code
            self.checksum = checksum

            self.bytes = struct.pack(
                self._FORMAT,
                self.message_type, 
                self.code,
                0x000,
                0,
                0,
                self.data
            )

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @bytes.setter
    def bytes(self, bytes_struct: bytes) -> None:
        self._bytes = bytes_struct

    @property
    def human_readable(self) -> tuple:
        return struct.unpack(self._FORMAT, self.bytes)

    @property
    def size(self) -> int:
        return len(self.bytes)
    
    @property
    def size_with_ip_header(self) -> int:
        return self.size + 20

    def __call__(self, id: int = 0, sequence_number: int = 0) -> Packet:
        mock_header = struct.pack(
            self._FORMAT,
            self.message_type, 
            self.code,
            0x000,
            id,
            sequence_number,
            self.data
        )

        self.checksum = self.calculate_checksum(mock_header)

        self.bytes = struct.pack(
            self._FORMAT,
            self.message_type, 
            self.code,
            self.checksum,
            id,
            sequence_number,
            self.data
        )

        return self

    def calculate_checksum(self, packet: bytes) -> int:
        if len(packet) % 2 != 0:
            packet += b'\0'  # asure that array lib will have always 2 bytes to work

        # 'H' unsigned short int
        res = sum(array.array("H", packet))  # sum array
        # shift bits by 16 and perform a logical and, also check if n bits are larger than 16
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16

        return (~res) & 0xffff  # compliment

    def is_valid(self, current_id: int, current_seq_number: int) -> bool:
        mock_packet = struct.pack(
            self._FORMAT,
            self.message_type, 
            self.code,
            0x000,
            self.id,
            self.sequence_number,
            self.data
        )

        to_be_tested = self.calculate_checksum(mock_packet)

        return self.checksum == to_be_tested and current_id == self.id and current_seq_number == self.sequence_number
        