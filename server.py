#!/usr/bin/env python3
from src.Config import Config
import conn_mongo
import socket
import json
import random
import threading
import time

HOST = '192.168.100.133'
PORT = 60000

# Data of settings
width_total = Config['game']['width']
width_able = Config['game']['width'] - Config['game']['bumper_size'] * 15
height_total = Config['game']['height']
height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
square_size = Config['game']['square_size']

def positions_def2():
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
    # Dictionary to json format
    datos = {
        "positions_free": positions_free,
        "positions": positions,
        "pos": [posP, posP2, posW]
    }

    return datos

def positions_def():
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

    return datos

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Port reusable
    s.bind((HOST, PORT))
    s.listen(30)

    dual_player = []
    contador_partidas = 0

    while True:
        conn, addr = s.accept()
        with conn:

            print('CONNECT WITH', addr)

            # RECIBIR
            comando = conn.recv(4096).decode()
            print(comando)
            print("Bytes: " + str(comando.__sizeof__()))

            # Envia posicion a modo invitado y al modo one player
            if comando == "verify_user":

                data_all = conn.recv(4096).decode()
                from_clt = json.loads(data_all)

                # True si existe o se creo el registro en mongoDb
                validar = conn_mongo.view_user(from_clt)

                if validar:
                    conn.send("ok".encode())
                else:
                    conn.send("no".encode())

            elif comando == "create_pos":

                # convert into JSON:
                datos_serial = json.dumps( positions_def() )
                conn.sendall(datos_serial.encode())

            elif comando == "send_points":

                data_all = conn.recv(4096).decode()

                from_clt = json.loads(data_all)

                conn_mongo.view_record(from_clt)

            elif comando == "connect_players":

                data_all = conn.recv(4096).decode()

                from_clt = json.loads(data_all)

                # Añado una lista en la lista dual_player, si esta vacia
                if len(dual_player) == 0:

                    dict_player = {
                        "p1": None,
                        "p2": None,
                        "p1_c": [0, 0],
                        "p2_c": [0, 0],
                        "match": contador_partidas,
                        "positions_m": positions_def2()
                    }

                    dual_player.append( dict_player )
                    contador_partidas += 1

                for player in dual_player:

                    if player["p1"] is None:
                        player["p1"] = from_clt["user_s"]

                    elif player["p2"] is None:
                        player["p2"] = from_clt["user_s"]

                        dict_player = {
                            "p1": None,
                            "p2": None,
                            "p1_c": [0, 0],
                            "p2_c": [0, 0],
                            "match": contador_partidas,
                            "positions_m": positions_def2()
                        }

                        dual_player.append( dict_player )
                        contador_partidas += 1
                        break

            # Envia posicion a modo multijugador
            elif comando == "verify_multi":

                data_all = conn.recv(4096).decode()
                from_clt = json.loads(data_all)

                encontrado = False

                for player in dual_player:

                    if player["p1"] is None or player["p2"] is None:
                        continue

                    if player["p1"] == from_clt["user_s"] or player["p2"] == from_clt["user_s"]:
                        conn.sendall( str( player["match"] ).encode() )
                        encontrado = True
                        break

                if not encontrado:
                    conn.sendall( "not_partner".encode())

            # Envia posicion a modo multijugador
            elif comando == "create_pos_multi":

                data_all = conn.recv(4096).decode()

                for player in dual_player:

                    if player["match"] == int(data_all):

                        dict_game = {
                            "p1": player["p1"],
                            "p2": player["p2"],
                            "positions_m": player["positions_m"]
                        }

                        positions_player = json.dumps( dict_game )
                        conn.sendall(positions_player.encode())
                        break

            elif comando == "get_change":

                data_all = conn.recv(4096).decode()
                from_clt = json.loads(data_all)

                for player in dual_player:

                    if player["p1"] is None or player["p2"] is None:
                        continue

                    if player["match"] == from_clt["match"]:

                        if from_clt["user_s"] == player["p1"]:
                            positions_send = {
                                "change_p1": player["p1_c"],
                                "change_p2": player["p2_c"]
                            }
                            changes_players = json.dumps(positions_send)
                            conn.sendall(changes_players.encode())

                        elif from_clt["user_s"] == player["p2"]:
                            positions_send = {
                                "change_p1": player["p2_c"],
                                "change_p2": player["p1_c"]
                            }
                            changes_players = json.dumps(positions_send)
                            conn.sendall(changes_players.encode())

            elif comando == "update_change":
                pass

            print("-"*30)

