#!/usr/bin/python3

import socket, argparse
from Xlib import display


def stream_mouse(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)

    screen = display.Display().screen()
    x, y = -1, -1

    while True:
        pointer = screen.root.query_pointer()
        last_x, last_y = x, y
        x, y = pointer.root_x, pointer.root_y
        s.send(f'{x},{y};'.encode())

def main():
    parser = argparse.ArgumentParser(
        description = "Stream mouse coordinates to a server via TCP")
    parser.add_argument('-host', type = str, default = 'localhost',
        help = 'Server hostname / IP')
    parser.add_argument('-port', type = int, default = 31444,
        help = 'Server port')
    args = parser.parse_args()

    stream_mouse((args.host, args.port))


if __name__ == "__main__":
    main()
