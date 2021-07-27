import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This program implements the ICMP (RFC 792).")

    parser.add_argument("-d", "--destination", help="The address to send the ECHO REPLY message.")

    return parser.parse_args()