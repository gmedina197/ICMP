import struct
from utils import send_echo
from cli_arguments import get_args

args = get_args()

send_echo(args.destination)

""" header = struct.pack("!BBHHB", ICMP_ECHO, CODE, 0, IDENTIFIER, 1)
data = 192 * 'Q'

check = checksum(header + bytes(data, "utf-8"))
print(hex(check)) """

#data = map(lambda x: int(x, 16), data)
#data = struct.pack("%dB" % size, *data)
