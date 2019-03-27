#!/usr/bin/env python3
from src.Config import Config
import conn_mongo
import socket
import json
import random

HOST = '127.0.0.1'
PORT = 60000

# Data of settings
width_total = Config['game']['width']
width_able = Config['game']['width'] - Config['game']['bumper_size'] * 15
height_total = Config['game']['height']
height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
square_size = Config['game']['square_size']

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Port reusable
    s.bind((HOST, PORT))
    s.listen(30)
    while True:
        conn, addr = s.accept()
        with conn:

            print('CONNECT WITH', addr)

            # RECIBIR
            comando = conn.recv(4096).decode()
            print(comando)
            print("Bytes: " + str(comando.__sizeof__()))

            # Envia posicion a modo invitado y al modo one player
            if comando == "create_pos":

                # Array multidimensional para posiciones (x, y)
                positions_free = [[e, f] for e in range(square_size,
                                                        width_able + square_size,
                                                        square_size)
                                  for f in range(square_size,
                                                 height_able + square_size,
                                                 square_size)]
                # Positions of player and goal
                posP = random.choice(positions_free)
                positions_free.remove(posP)

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
                positions_free.append(posW)
                # Dictionary to json format
                datos = {
                    "positions_free": positions_free,
                    "positions": positions,
                    "pos": [posP, posW]
                }
                # convert into JSON:
                datos_serial = json.dumps(datos)
                conn.sendall( datos_serial.encode() )

            # Envia posicion a modo multijugador
            elif comando == "create_pos_multi":

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

            elif comando == "update_pos":
                pass

            elif comando == "send_points":

                data_all = conn.recv(4096).decode()

                from_clt = json.loads(data_all)

                conn_mongo.view_record(from_clt)

            elif comando == "verify_user":

                data_all = conn.recv(4096).decode()

                from_clt = json.loads(data_all)

                # True si existe o se creo el registro en mongoDb
                validar = conn_mongo.view_user(from_clt)

                if validar:
                    conn.send("ok".encode())
                else:
                    conn.send("no".encode())

            print("-----")
