import socket
import struct
import array
import time
import math

ICMP_CODE = socket.getprotobyname('icmp')

ICMP_ECHO = 8
ICMP_ECHO_REPLY = 0

CODE = 0
IDENTIFIER = 0
SEQUENCE_NUMBER = 0


STRUCT_FORMAT = "!BBHHH"

__BUFFER_SIZE__ = 1024

def create_raw_socket() -> socket.socket:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)

        return s
    except socket.error as e:
        print(f"error creating socket. Code: {str(e[0])}. message: {e[1]}")


def checksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'  # asure that array lib will have always 2 bytes to work

    # 'H' unsigned short int
    res = sum(array.array("H", packet))  # sum array
    # shift bits by 16 and perform a logical and, also check if bits are more than 16
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff  # compliment

def create_packet() -> bytes:
    #! network (= big-endian)
    # B unsigned char (8 bits)
    # H unsigned short (16 bits)
    
    data = b"pong:)" # dummy data

    header = struct.pack("!BBHHH6s", ICMP_ECHO, CODE, 0, IDENTIFIER, 1, data)

    check = checksum(header)

    header = struct.pack("!BBHHH6s", ICMP_ECHO, CODE, socket.htons(check), IDENTIFIER, 1, data)

    return header

def send_echo(dest_addr: str):

    # VERIFY IDS AND SEQUENCE NUMBER
    # CALC RTT
    # PACKAGE LOSS

    raw_socket = create_raw_socket()

    try:
        host = socket.gethostbyname(dest_addr)
    except socket.gaierror as e:
        return

    packet = create_packet()

    print(f"PING {dest_addr} ({host}) {len(packet)}({len(packet) + 20}) bytes of data.")

    icmp_seq = 1
    while True:
        time_start = time.time()

        raw_socket.sendto(packet, (host, 1))

        recv_packet, addr = raw_socket.recvfrom(__BUFFER_SIZE__)
            
        icmp_header = recv_packet[20:28] # because of ipv4 header (20 bytes)

        fields = struct.unpack(STRUCT_FORMAT, icmp_header)
        
        elapsed_time = time.time() - time_start

        print(f"recv {fields}")
        print(addr)

        print(f"{len(recv_packet)} bytes from {dest_addr} ({host}): icmp_seq={icmp_seq} time={round(elapsed_time * 1000, 2)} ms")
        time.sleep(2)
        icmp_seq = icmp_seq + 1

    raw_socket.close()

def reply_echo():
    # EVERYTHING
    pass