import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This program implements the ICMP (RFC 792).")

    parser.add_argument("-d", "--destination", help="The address to send the ECHO REPLY message.")

    parser.add_argument("-v", "--verbose", help="Show a more detailed outuput.", nargs='?', const=True)
    
    parser.add_argument("-V", "--version", help="Show the version.", nargs='?', const=True)

    return parser.parse_args()