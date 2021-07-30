import socket
import struct
import array
import time
import select
import statistics

#from sys import getsizeof

ICMP_CODE = socket.getprotobyname('icmp')

ICMP_ECHO = 8
ICMP_ECHO_REPLY = 0

CODE = 0

__BUFFER_SIZE__ = 1024

HOTKEY = "ctrl + c"

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

def create_packet(id: int = 0, seq_number: int = 0) -> bytes:
    #! network (= big-endian)
    # B unsigned char (8 bits)
    # H unsigned short (16 bits)
    
    data = b"pong:)" # dummy data

    header = struct.pack("!BBHHH6s", ICMP_ECHO, CODE, 0, id, seq_number, data)

    check = checksum(header)

    header = struct.pack("!BBHHH6s", ICMP_ECHO, CODE, socket.htons(check), id, seq_number, data)

    return header

def echo_statistics(dest_addr: str, icmp_seq: int, received: int, total_time, times: list):
    package_loss = (100 / icmp_seq) * (icmp_seq - received)

    print("\n")
    print(f"--- {dest_addr} ping statistics ---")
    print(f"{icmp_seq} packets transmitted, {received} received, {round(package_loss)}% packet_loss, {round(total_time * 1000, 2)}ms")

    print(f"rtt min/avg/max/mdev = {min(times)}/{round(statistics.mean(times), 3)}/{max(times)}/{round(statistics.stdev(times), 3)} ms")

def send_echo(dest_addr: str, timeout: float = 2, verbose: bool = False):

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

    icmp_seq = 0
    received = 0

    times = []
    total_time = time.time()
    while True:
        try:

            time_start = time.time()

            #id = random.getrandbits(16)
                        
            packet = create_packet(seq_number=icmp_seq)

            raw_socket.sendto(packet, (host, 1))

            icmp_seq = icmp_seq + 1

            not_timeout = select.select([raw_socket], [], [], timeout)

            if not_timeout[0]:
                recv_packet, addr = raw_socket.recvfrom(__BUFFER_SIZE__) #only move foward if package is received
                received = received + 1

                a,b,c,d = struct.unpack("!BBBB", recv_packet[12:16])

                source_addr = socket.gethostbyaddr(f"{a}.{b}.{c}.{d}")

                icmp_header = recv_packet[20:28] #because of ipv4 header (20 bytes)
                
                message_type, code, chcksum, icmp_id, seq = struct.unpack("!BBHHH", icmp_header)
                
                elapsed_time = time.time() - time_start

                formatted_time = round(elapsed_time * 1000, 2)
                times.append(formatted_time)

                print(f"{len(recv_packet)} bytes from {source_addr} ({host}): icmp_seq={icmp_seq} time={formatted_time}ms")
            elif verbose:
                print(f"({host}): icmp_seq={icmp_seq} timed out after 2000ms")

            time.sleep(1)

        except KeyboardInterrupt:
            raw_socket.close()
            echo_statistics(dest_addr, icmp_seq, received, time.time() - total_time, times)
            return

def reply_echo():
    # EVERYTHING
    pass
