#!/usr/bin/python3

import socket
from rgbmatrix import Adafruit_RGBmatrix as RGBmatrix
from PIL import Image

matrix = RGBmatrix(32, 2)
img = Image("RGB", (64, 32), (0, 0, 3))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 31444))
s.listen(1)

while True:
    client_socket, address = s.accept()
    
    while True:
        
        data = client_socket.recv(1024).decode()
        if len(data) == 0:
            break
                
        messages = data.split(';')
        data = messages[-1]
        messages = messages[:-1]
        
        for message in messages:
            coords = message.split(',')
            x = int(coords[0]) * 64
            y = int(coords[1]) * 32
            img.setPixel((x, y), (127, 127, 127))
        
        matrix.SetImage(img.im.id)
    
    client_socket.close()
