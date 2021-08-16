from packet import Packet
import socket
import struct
import time
import select
import statistics
import random

ICMP_ECHO = 8
CODE = 0

def create_raw_socket() -> socket.socket:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))

        return s
    except socket.error as e:
        print(f"error creating socket. Code: {str(e[0])}. message: {e[1]}")

def echo_statistics(dest_addr: str, icmp_seq: int, received: int, total_time, times: list):
    package_loss = (100 / icmp_seq) * (icmp_seq - received)

    print("\n")
    print(f"--- {dest_addr} ping statistics ---")
    print(f"{icmp_seq} packets transmitted, {received} received, {round(package_loss)}% packet_loss, {round(total_time * 1000, 2)}ms")
    
    if times:
        print(f"rtt min/avg/max/mdev = {min(times)}/{round(statistics.mean(times), 2)}/{max(times)}/{round(statistics.stdev(times), 2)} ms")


create_packet = Packet(b"pong:)", ICMP_ECHO, CODE)
def send_echo(dest_addr: str, timeout: float = 2, verbose: bool = False):
    raw_socket = create_raw_socket()

    try:
        host = socket.gethostbyname(dest_addr)
    except socket.gaierror as e:
        print("Cannot found a valid hostname for that.")
        return 

    mock_packet = create_packet()

    print(f"PING {dest_addr} ({host}) {mock_packet.size}({mock_packet.size_with_ip_header}) bytes of data.")

    icmp_seq = 0
    received = 0

    times = []
    total_time = time.time()

    id = random.getrandbits(16)

    while True:
        try:

            time_start = time.time()
                        
            packet = create_packet(id=id, sequence_number=icmp_seq)

            raw_socket.sendto(packet.bytes, (host, 1))

            not_timeout = select.select([raw_socket], [], [], timeout)

            if not_timeout[0]:
                recv_packet, addr = raw_socket.recvfrom(1024) #only move foward if package is received

                # RTT
                elapsed_time = time.time() - time_start

                formatted_time = round(elapsed_time * 1000, 2)
                times.append(formatted_time)
                ########

                ### Validation and output
                a, b, c, d = struct.unpack("BBBB", recv_packet[12:16])

                source_addr = socket.gethostbyaddr(f"{a}.{b}.{c}.{d}")

                icmp_header = Packet(bytes=recv_packet[20:]) #because of ipv4 header (20 bytes)

                if icmp_header.is_valid(id, icmp_seq):
                    received = received + 1
                    print(f"{len(recv_packet)} bytes from {source_addr[0]} ({host}): icmp_seq={icmp_seq} time={formatted_time}ms")
            
            elif verbose:
                print(f"({host}): icmp_seq={icmp_seq} timed out after 2000ms")

            icmp_seq = icmp_seq + 1

            time.sleep(1)

        except KeyboardInterrupt:
            raw_socket.close()
            echo_statistics(dest_addr, icmp_seq, received, time.time() - total_time, times)
            return
