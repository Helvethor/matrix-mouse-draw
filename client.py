#!/usr/bin/python3

import socket, argparse, time
from Xlib import display
from pynput import mouse


class MouseStreamer:


    def __init__(self, server_address):
        self.color = [127, 127, 127]
        self.server_address = server_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(server_address)

    def send(self, data):
        self.socket.send((data + ';').encode())

    def on_move(self, x, y):
        self.send(f'cursor:{x / 1920 / 2},{y / 1080},{self.color[0]},{self.color[1]},{self.color[2]}')

    def on_click(self, x, y, button, press):

        if press:
            if button == mouse.Button.left:
                self.color[0] = 255
            elif button == mouse.Button.right:
                self.color[1] = 255
            elif button == mouse.Button.middle:
                self.color[2] = 255
        else:
            if button == mouse.Button.left:
                self.color[0] = 127
            elif button == mouse.Button.right:
                self.color[1] = 127
            elif button == mouse.Button.middle:
                self.color[2] = 127

        self.on_move(x, y)

    def on_scroll(self, x, y, dx, dy):
        direction = 'v' if dy != 0 else 'h'
        sign = '+' if dx + dy > 0 else '-'
        self.send(f'scroll:{direction}{sign}')

    def stream(self):
        kwargs = {
            'on_move': self.on_move,
            'on_click': self.on_click,
            'on_scroll': self.on_scroll
        }

        with mouse.Listener(**kwargs) as listener:
            listener.join()


def main():
    parser = argparse.ArgumentParser(
        description = "Stream mouse coordinates to a server via TCP")
    parser.add_argument('-host', type = str, default = 'localhost',
        help = 'Server hostname / IP')
    parser.add_argument('-port', type = int, default = 31444,
        help = 'Server port')
    args = parser.parse_args()

    while True:
        try:
            mouse_streamer = MouseStreamer((args.host, args.port))
            print('Connected')
            mouse_streamer.stream()
        except (ConnectionResetError, BrokenPipeError) as e:
            print('Connection reset, retrying in 1 second')
            time.sleep(1)
        except ConnectionRefusedError as e:
            print('Connection refused, retrying in 1 second')
            time.sleep(1)


if __name__ == "__main__":
    main()
