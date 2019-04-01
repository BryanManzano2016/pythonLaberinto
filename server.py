#!/usr/bin/env python3
from src.Config import Config
import conn_mongo
import socket
import json
import random

HOST = '192.168.100.133'
PORT = 60000

# Data of settings
width_total = Config['game']['width']
width_able = Config['game']['width'] - Config['game']['bumper_size'] * 15
height_total = Config['game']['height']
height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
square_size = Config['game']['square_size']

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

    '''
    dual_player: Lista de diccionarios, los cuales contienen datos de la partida ( player 1 y 2, nro partida, posiciones 
    iniciales de laberinto
    contador_partidas: numero de partida que se modifica con cada nuevo enlace multijugador
    '''
    dual_player = []
    users = set()
    contador_partidas = 0

    while True:
        conn, addr = s.accept()
        with conn:

            # String con la peticion que se hace al cliente y numero de bits
            comando = conn.recv(256).decode()

            comando_split = comando.split("_")
            if len(comando_split) != 2:
                comando = comando_split[0] + "_" +  comando_split[1]

            # print(comando)
            # print("Bytes: " + str(comando.__sizeof__()))

            # Valida que exista usuario (si no, lo crea), ademas no pueden crearse 2 partidas con un mismo user
            if comando == "verify_user":

                data_all = conn.recv(256).decode()

                from_clt = json.loads(data_all)

                # True si existe o se creo el registro en mongoDb o estan en users activos
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
                    conn.send("ok".encode())
                    users.add(from_clt["user_s"])
                else:
                    conn.send("no".encode())
            # Añade un jugador al diccionario, debido a que esta en linea actualmente
            elif comando == "append_user":

                data_all = conn.recv(256).decode()
                users.add(data_all)

            # Posiciones para modo one-player e invitado
            elif comando == "create_pos":

                # convert into JSON:
                datos_serial = json.dumps( positions_def() )
                conn.sendall(datos_serial.encode())

            # Modo one-player envia un record a la base de datos, si es mayor al anterior lo sustituye
            elif comando == "send_points":

                data_all = conn.recv(256).decode()

                from_clt = json.loads(data_all)
                conn_mongo.view_record(from_clt)

            # Enlaza jugadores en multiplayer y crea los parametros del laberinto inicial
            elif comando == "connect_players":

                data_all = conn.recv(256).decode()
                from_clt = json.loads(data_all)

                # Añado una lista (datos de partida) en la lista dual_player, si esta vacia
                if len(dual_player) == 0:
                    '''
                    p1: nombre de usuario 1
                    p2: nombre de usuario 2
                    p1_c: posicion de usuario 1
                    p2_c: posicion de usuario 2
                    match: nro de la partida
                    positions_m: posiciones de laberinto e iniciales de los jugadores
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
                        "status": True
                    }

                    dual_player.append( dict_player )
                    contador_partidas += 1

                for player in dual_player:

                    if player["p1"] is None:
                        player["p1"] = from_clt["user_s"]
                        break

                    elif player["p2"] is None:
                        player["p2"] = from_clt["user_s"]

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
                            "status": True
                        }

                        dual_player.append( dict_player )
                        contador_partidas += 1
                        break

            # Verifica que exista una partida multiplayer para el cliente y envia el numero de partida
            elif comando == "verify_multi":

                data_all = conn.recv(256).decode()
                from_clt = json.loads(data_all)

                encontrado = False

                for player in dual_player:

                    if player["p1"] is None or player["p2"] is None or player["p1"] != from_clt["user_s"] or \
                            player["p2"] != from_clt["user_s"]:
                        continue

                    if player["p1"] == from_clt["user_s"] or player["p2"] == from_clt["user_s"]:
                        conn.sendall( str( player["match"] ).encode() )
                        encontrado = True
                        break

                if not encontrado:
                    conn.sendall( "not_partner".encode())

            # Envia posicion a modo multijugador
            elif comando == "create_posMulti":

                data_all = conn.recv(256).decode()
                for player in dual_player:

                    if int(data_all) != player["match"]:
                        continue
                    elif player["match"] == int(data_all):

                        # Envia el nombre del usuario oponente y las posiciones iniciales del laberinto
                        dict_game = {
                            "p1": player["p1"],
                            "p2": player["p2"],
                            "positions_m": player["positions_m"]
                        }

                        positions_player = json.dumps( dict_game )
                        conn.sendall(positions_player.encode())
                        break

            # Si algun jugador termina la partida, se elimina la partida (diccionario en lista dual_player) de la lista
            elif comando == "delete_match":

                data_all = conn.recv(256).decode()
                for player in dual_player:

                    if player["match"] != int(data_all):
                        continue
                    elif player["match"] == int(data_all):

                        if player["p1_points"] > player["p2_points"]:
                            conn_mongo.set_result(player["p1"], player["p2"], player["p1"])
                        if player["p1_points"] < player["p2_points"]:
                            conn_mongo.set_result(player["p1"], player["p2"], player["p2"])

                        dual_player.remove(player)
                        break

            # Elimina un jugador del diccionario, debido a que salio del juego
            elif comando == "delete_user":

                data_all = conn.recv(256).decode()
                users.remove(data_all)

            # Recupera la posicion rival
            elif comando == "get_change":
                # Oponente oponente y nro de partida
                oponent = comando_split[2]
                match =  int(comando_split[3])
                # if la partida no existe
                not_found_match = True

                for player in dual_player:

                    if match != player["match"]:
                        continue

                    # Diccionario para enviar la posicion del oponente
                    dict_change = {
                        "change": None
                    }

                    if oponent == "p1":

                        dict_change["change"] = player["p1_c"]
                        changes_player = json.dumps(dict_change)

                        conn.send(changes_player.encode())
                        not_found_match = False

                    elif oponent == "p2":

                        dict_change["change"] = player["p2_c"]
                        changes_player = json.dumps(dict_change)

                        conn.send(changes_player.encode())
                        not_found_match = False

                if not_found_match:
                    conn.send( "not_match".encode())

            #Actualiza la posicion del jugador
            elif comando == "update_change":
                # Extra oponente, nro de partida y posiciones actuales del jugador para actualizar dichas posiciones
                player_n = comando_split[2]
                match = int(comando_split[3])
                c_x = int(comando_split[4])
                c_y = int(comando_split[5])

                for player in dual_player:

                    if match != player["match"]:
                        continue

                    if player_n == "p1":
                        player["p1_c"] = [ c_x, c_y]
                    elif player_n == "p2":
                        player["p2_c"] = [ c_x, c_y]

            elif comando == "send_winner":

                data_all = conn.recv(256).decode()

                from_clt = json.loads(data_all)

                for player in dual_player:

                    if player["p1"] is None or player["p2"] is None or int( from_clt["match"] ) != player["match"]:
                        continue

                    if from_clt["winner"] == player["p1"]:
                        player["p1_points"] += 1
                    elif from_clt["winner"] == player["p2"]:
                        player["p2_points"] += 1

                    p1_c, p2_c, positions_m = set_new_pos()
                    player["p1_c"] = p1_c
                    player["p2_c"] = p2_c
                    player["positions_m"] = positions_m

            elif comando == "send_restart":

                data_all = int( conn.recv(256).decode() )

                for player in dual_player:

                    if player["match"] != data_all:
                        continue
                    elif player["match"] == data_all:

                        p1_c, p2_c, positions_m = set_new_pos()
                        player["p1_c"] = p1_c
                        player["p2_c"] = p2_c
                        player["positions_m"] = positions_m

            # Print de prueba
            if comando != "get_change" and comando != "update_change":
                print('CONNECT WITH', addr)
                print(comando)
                print(users)
                for pl in dual_player:
                    print(pl["match"])
                    print(pl["p1"], " ,", pl["p1_c"], " ,", pl["p1_points"])
                    print(pl["p2"], " ,", pl["p2_c"], " ,", pl["p2_points"])
                print("-"*50)