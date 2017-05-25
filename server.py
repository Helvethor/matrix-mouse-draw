#!/usr/bin/python3

import socket, threading, queue, math, time
from rgbmatrix import Adafruit_RGBmatrix as RGBmatrix
from PIL import Image


class MousePainter:

    def __init__(self, messages):

        self.messages = messages
        self.matrix = RGBmatrix(32, 2)
        self.img = Image.new("RGB", (64, 32), (0, 0, 0))
        self.cursors = []
        self.cursor_timeout = 1

    def paint(self):
        
        while True:

            while not self.messages.empty():
                try:
                    message = self.messages.get_nowait()
                    self.handle(message)
                except queue.Empty as e:
                    break

            self.img = self.img.point(lambda p: 0)

            self.update_cursors()
            self.paint_cursors()

            self.matrix.SetImage(self.img.im.id)
            time.sleep(1 / 120)

    def update_cursors(self):
        now = time.time()
        self.cursors = [{
            'pos': cursor['pos'],
            'color': cursor['color'],
            'creation_time': cursor['creation_time'],
            'update_time': now
            } for cursor in self.cursors
            if now - cursor['creation_time'] < self.cursor_timeout]

    def paint_cursors(self):
        now = time.time()
        for cursor in self.cursors: 
            color_base = cursor['color']
            color_intensity = 1 - (cursor['update_time'] - cursor['creation_time']) / self.cursor_timeout
            color = tuple([math.floor(c * color_intensity) for c in color_base])
            self.img.putpixel(cursor['pos'], color)

    def handle(self, message):
        action, payload = message.split(':')

        if action == 'cursor':
            parts = payload.split(',')
            x = int(float(parts[0]) * 64)
            y = int(float(parts[1]) * 32)
            color = tuple(map(int, parts[2:]))
            if len(self.cursors) > 0 and (x, y) == self.cursors[-1]['pos']:
                self.cursors[-1]['color'] = color
                self.cursors[-1]['creation_time'] = time.time()
            else:
                self.cursors.append({
                    'pos': (x, y),
                    'color': color,
                    'creation_time': time.time()
                })

        elif action == 'scroll':
            if payload[1] == '-' and self.cursor_timeout > 0.5:
                if payload[0] == 'v':
                    self.cursor_timeout *= 0.9
                elif payload[0] == 'h':
                    pass
            elif payload[1] == '+' and self.cursor_timeout < 4:
                if payload[0] == 'v':
                    self.cursor_timeout *= 1.1
                elif payload[0] == 'h':
                    pass      


class ServerThread(threading.Thread):

    def __init__(self, messages):

        super().__init__()
        self.messages = messages
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 31444))
        self.socket.listen(1)

    def run(self):
        client_socket, address = self.socket.accept()
        data = ''

        while True:
            read_data = client_socket.recv(1024).decode()
            if len(read_data) == 0:
                break

            data += read_data
            messages = data.split(';')
            data = messages[-1]
            messages = messages[:-1]
        
            [self.messages.put(m) for m in messages]

        client_socket.close()


messages = queue.Queue()
server = ServerThread(messages)
server.start()
mouse_painter = MousePainter(messages)
mouse_painter.paint()
