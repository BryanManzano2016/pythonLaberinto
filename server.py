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

dual_player = []
users = set()
contador_partidas = 0

class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            for player_t in dual_player:
                if player_t["p1"] is None or player_t["p2"] is None:
                    continue
                elif player_t["seconds"] >= 50 and player_t["restart"] == 0:
                    p1_c1, p2_c2, positions_m1 = set_new_pos()
                    player_t["p1_c"] = p1_c1
                    player_t["p2_c"] = p2_c2
                    player_t["positions_m"] = positions_m1
                    player_t["restart"] = 2
                else:
                    player_t["seconds"] += 1
            time.sleep(1)

# Retorna posiciones para multijugador
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

def set_new_pos():

    positions_conn_2 = positions_def2()

    return positions_conn_2["pos"][0], positions_conn_2["pos"][1], positions_conn_2

# Retorna posiciones para one-player e invitado
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

# Verifica que el usuario no este en juego actualmente con la sesion del servidor
def verify_match(dicts, user):
    for dt in dicts:
        if user == dt["p1"] or user == dt["p2"]:
            return True
        else:
            return False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Port reusable
    s.bind((HOST, PORT))
    s.listen(30)

    time_restart = myThread()
    time_restart.start()

    '''
    dual_player: Lista de diccionarios, los cuales contienen datos de la partida ( player 1 y 2, nro partida, posiciones 
    iniciales de laberinto
    contador_partidas: numero de partida que se modifica con cada nuevo enlace multijugador
    '''

    while True:
        conn, addr = s.accept()
        with conn:

            # String con la peticion que se hace al cliente y numero de bits
            data_cliente = conn.recv(256).decode()
            recv_json = json.loads(data_cliente)

            # Valida que exista usuario (si no, lo crea), ademas no pueden crearse 2 partidas con un mismo user
            if recv_json["comando"] == "verify_user":

                # True si existe o se creo el registro en mongoDb o estan en users activos
                from_clt = {
                    "user_s": recv_json["user_s"],
                    "pass_s": recv_json["pass_s"]
                }

                validar = conn_mongo.view_user(from_clt)
                validar2 = verify_match(dual_player, from_clt["user_s"])
                validar3 = False

                for element in users:
                    if element == from_clt["user_s"]:
                        validar3 = True

                '''
                    Valida que no existan en la sesion 2 jugadores con nombre igual y que se cree un usuario con un user
                    igual
                '''
                if validar and not validar2 and not validar3:
                    conn.sendall("ok".encode())
                    users.add(from_clt["user_s"])
                else:
                    conn.sendall("no".encode())

            # Añade un jugador al diccionario, debido a que esta en linea actualmente
            elif recv_json["comando"] == "append_user":
                users.add( recv_json["user_s"] )

            # Posiciones para modo one-player e invitado
            elif recv_json["comando"] == "create_pos":

                datos_serial = json.dumps( positions_def() )
                conn.sendall(datos_serial.encode())

            # Modo one-player envia un record a la base de datos, si es mayor al anterior lo sustituye
            elif recv_json["comando"] == "send_points":

                from_clt = {
                    "user_s": recv_json["user_s"],
                    "pass_s": recv_json["pass_s"],
                    "record": recv_json["record"]
                }

                conn_mongo.view_record(from_clt)

            # Enlaza jugadores en multiplayer y crea los parametros del laberinto inicial
            elif recv_json["comando"] == "connect_players":

                # Añado una lista (datos de partida) en la lista dual_player, si esta vacia
                if len(dual_player) == 0:
                    '''
                    p1: nombre de usuario 1
                    p2: nombre de usuario 2
                    p1_c: posicion de usuario 1
                    p2_c: posicion de usuario 2
                    match: nro de la partida
                    positions_m: posiciones de laberinto e iniciales de los jugadores
                    restart_time: _n el jugador n debe reiniciar
                    restart_win: _n n gano la partida
                    '''
                    p1_c, p2_c, positions_m = set_new_pos()

                    dict_player = {
                        "p1": None,
                        "p2": None,
                        "p1_c": p1_c,
                        "p2_c": p2_c,
                        "p1_points": 0,
                        "p2_points": 0,
                        "match": contador_partidas,
                        "positions_m": positions_m,
                        "restart": 0,
                        "last_restart": "",
                        "seconds": 0
                    }

                    dual_player.append( dict_player )
                    contador_partidas += 1

                for player in dual_player:

                    if player["p1"] is None:
                        player["p1"] = recv_json["user_s"]
                        break

                    elif player["p2"] is None:
                        player["p2"] = recv_json["user_s"]

                        p1_c, p2_c, positions_m = set_new_pos()

                        dict_player = {
                            "p1": None,
                            "p2": None,
                            "p1_c": p1_c,
                            "p2_c": p2_c,
                            "p1_points": 0,
                            "p2_points": 0,
                            "match": contador_partidas,
                            "positions_m": positions_m,
                            "restart": 0,
                            "last_restart": "",
                            "seconds": 0
                        }

                        dual_player.append( dict_player )
                        contador_partidas += 1
                        break

            # Verifica que exista una partida multiplayer para el cliente y envia el numero de partida
            elif recv_json["comando"] == "verify_multi":

                encontrado = False

                dict_send = dict()

                for player in dual_player:

                    if player["p1"] is None or player["p2"] is None:
                        continue

                    if player["p1"] == recv_json["user_s"] or player["p2"] == recv_json["user_s"]:
                        dict_send["match"] = player["match"]
                        dict_send["match"] = player["match"]
                        conn.sendall( ( json.dumps(dict_send) ).encode() )
                        encontrado = True
                        break

                if not encontrado:
                    dict_send["match"] = -1
                    conn.sendall( json.dumps(dict_send).encode() )

            # Envia posicion a modo multijugador
            elif recv_json["comando"] == "create_posMulti":

                for player in dual_player:

                    if recv_json["match"] != player["match"]:
                        continue

                    elif player["match"] == recv_json["match"]:

                        # Envia el nombre del usuario oponente y las posiciones iniciales del laberinto
                        dict_game = {
                            "p1": player["p1"],
                            "p2": player["p2"],
                            "positions_m": player["positions_m"]
                        }

                        positions_player = json.dumps( dict_game )
                        conn.sendall( positions_player.encode() )

                        break

            # Recupera la posicion rival
            elif recv_json["comando"] == "get_change":
                # if la partida no existe
                not_found_match = True

                for player in dual_player:

                    if recv_json["match"] != player["match"]:
                        continue

                    # Diccionario para enviar la posicion del oponente
                    dict_change = {
                        "change_p1": None,
                        "change_p2": None
                    }

                    not_found_match = False

                    if player["last_restart"] != recv_json["nro_player"] and player["restart"] != 0:
                        conn.sendall("reboot".encode())
                        player["restart"] -= 1
                        player["seconds"] = 0
                        player["last_restart"] = recv_json["nro_player"]
                    elif player["restart"] < 2:
                        dict_change["change_p1"] = player["p1_c"]
                        dict_change["change_p2"] = player["p2_c"]
                        # Envia la posicion del rival
                        conn.sendall( (json.dumps(dict_change)).encode())
                    break

                # Le envia que ya no existe la partida, el oponente cierra
                if not_found_match:
                    conn.sendall( "not_match".encode())

            # Actualiza la posicion del jugador, si gana reinicia el laberinto
            elif recv_json["comando"] == "update_change":

                winner = -1

                for player in dual_player:

                    if recv_json["match"] != player["match"]:
                        continue

                    elif recv_json["nro_player"] == "p1":
                        player["p1_c"] = [ recv_json["change"][0], recv_json["change"][1]]
                        # Si llega a la meta
                        if player["p1_c"] == player["positions_m"]["pos"][2]:
                            player["p1_points"] += 1
                            # El jugador oponente debe reiniciar
                            player["restart"] = 2
                            winner = recv_json["match"]

                    elif recv_json["nro_player"] == "p2":
                        player["p2_c"] = [ recv_json["change"][0], recv_json["change"][1]]
                        if player["p2_c"] == player["positions_m"]["pos"][2]:
                            player["p2_points"] += 1
                            player["restart"] = 2
                            winner = recv_json["match"]

                    break

                for player in dual_player:
                    if player["match"] != winner:
                        continue
                    elif player["match"] == winner:
                        p1_c, p2_c, positions_m = set_new_pos()
                        player["p1_c"] = p1_c
                        player["p2_c"] = p2_c
                        player["positions_m"] = positions_m
                        break

            # Si algun jugador termina la partida, se elimina la partida (diccionario en lista dual_player) de la lista
            elif recv_json["comando"] == "delete_match":

                data_all = conn.recv(256).decode()
                for player in dual_player:

                    if player["match"] != recv_json["match"]:
                        continue
                    elif player["match"] == recv_json["match"]:

                        if player["p1_points"] > player["p2_points"]:
                            pass
                            # conn_mongo.set_result(player["p1"], player["p2"], player["p1"])
                        if player["p1_points"] < player["p2_points"]:
                            pass
                            # conn_mongo.set_result(player["p1"], player["p2"], player["p2"])

                        users.remove(player["p1"])
                        users.remove(player["p2"])
                        dual_player.remove(player)
                        break

            # Uso de modo user para login
            elif recv_json["comando"] == "delete_user":

                users.remove(recv_json["user_s"])
            '''
            if recv_json["comando"] != "get_change" and recv_json["comando"] != "update_change":
                print(users)
                print(len(dual_player))
                for pl in dual_player:
                    if not pl["p1"] is None or not pl["p2"] is None:
                        print('CONNECT WITH', " ", addr, ", ", recv_json["comando"])
                        print(pl["restart"], " :restart")
                        print(pl["p1"], " ,", pl["p1_c"], " ,", pl["p1_points"])
                        print(pl["p2"], " ,", pl["p2_c"], " ,", pl["p2_points"])
                print("-" * 50)
            '''

