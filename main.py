from utils import send_echo
from cli_arguments import get_args

args = get_args()

if args.version:
    print("Version 0.0.2alpha")
elif args.destination:
    send_echo(args.destination, verbose=args.verbose)
else:
    print("Required to pass a destination")
    print("e.g. main.py -d unioeste.br")