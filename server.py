#!/usr/bin/env python3
from time import sleep
from src.Config import Config
import socket
import json
import random

HOST = '127.0.0.1'
PORT = 60000

width_total = Config['game']['width']
width_able = Config['game']['width'] - Config['game']['bumper_size'] * 15
height_total = Config['game']['height']
height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
square_size = Config['game']['square_size']

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Port reusable
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
                print('Connected by', addr)
                positions_free = [[e, f] for e in range(square_size,
                                                        width_able + square_size,
                                                        square_size)
                                  for f in range(square_size,
                                                 height_able + square_size,
                                                 square_size)]

                posP = random.choice(positions_free)
                positions_free.remove(posP)

                posP2 = random.choice(positions_free)
                positions_free.remove(posP2)

                posW = random.choice(positions_free)
                positions_free.remove(posW)

                count_sq = 0
                positions = list()
                while count_sq < Config['game']['number_squares']:
                    posObj = random.choice(positions_free)
                    positions_free.remove(posObj)
                    positions.append(posObj)
                    count_sq += 1

                positions_free.append(posP)
                positions_free.append(posP2)
                positions_free.append(posW)

                datos = {
                    "positions_free": positions_free,
                    "positions": positions,
                    "pos": [posP, posP2, posW]
                }
                # convert into JSON:
                datos_serial = json.dumps(datos)
                conn.sendall( datos_serial.encode() )
