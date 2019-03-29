import pygame
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config
import socket
import json
import time

# Modo multijugador
HOST = '192.168.100.133'
PORT = 60000

class Game:

    def __init__(self, display, user_g):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']*15
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
        self.square_size = Config['game']['square_size']

        self.score = 0
        self.segundo = 0

        self.user = user_g
        self.num_match = None

        self.loop()

    def loop(self):

        clock = pygame.time.Clock()

        self.num_match = self.verify_multi()

        while self.num_match == "not_partner":

            time.sleep(3)
            self.num_match = self.verify_multi()

        print(self.num_match)

        posit = self.lists()

        positions_free = posit["positions_m"]["positions_free"]
        positions = posit["positions_m"]["positions"]

        posP = list()
        posP2 = list()

        if self.user["user_s"] == posit["p1"]:
            posP = posit["positions_m"]["pos"][0]
            posP2 = posit["positions_m"]["pos"][1]
        elif self.user["user_s"] == posit["p2"]:
            posP = posit["positions_m"]["pos"][1]
            posP2 = posit["positions_m"]["pos"][0]

        print(len(posP))
        print(len(posP2))

        #Creacion y ubicacion de jugadores y meta
        player_1 = Player(self.display, posP)
        player_2 = Player(self.display, posP2)

        players = list()
        players.append(player_1)
        players.append(player_2)

        posW = posit["positions_m"]["pos"][2]
        pointWin = PointWin(self.display, posW)

        # Una copia del tiempo transcurrido
        segundo_ant = -2

        while True:

            # Segundos transcurriendo de haber iniciado pygame
            segundo_act = int(pygame.time.get_ticks()) // 1000
            # Si la copia y los segundos actuales son diferentes
            if segundo_act != segundo_ant:
                segundo_ant = segundo_act
                self.segundo += 1
            #El contador global de segundos llega a 30 y reinicia la partida
            if self.segundo == 60:
                self.segundo = 0
                self.loop()

            #pos_c = self.get_changes()
            #pos_change = [pos_c["change_p1"], pos_c["change_p2"]]
            pos_change = [[0, 0], [0, 0]]

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        pos_change[0][0] += -self.square_size
                        pos_change[0][1] = 0
                        # pos_change[0]

                    elif event.key == pygame.K_RIGHT:
                        pos_change[0][0] += self.square_size
                        pos_change[0][1] = 0

                    elif event.key == pygame.K_UP:
                        pos_change[0][0] = 0
                        pos_change[0][1] += -self.square_size

                    elif event.key == pygame.K_DOWN:
                        pos_change[0][0] = 0
                        pos_change[0][1] += self.square_size

            # Fill background and draw game area
            self.display.fill(Config['colors']['green'])

            # Rectangulo blanco de juego
            pygame.draw.rect(
                self.display,
                Config['colors']['white'],
                [
                    self.square_size,
                    self.square_size,
                    self.width_able,
                    self.height_able
                ]
            )

            for x in positions:
                pygame.draw.rect(
                    self.display,
                    Config['colors']['black'],
                    [
                        x[0],
                        x[1],
                        self.square_size,
                        self.square_size
                    ]
                )

            for playerN in range(1):

                if (players[playerN].movimientoValido(pos_change[playerN], positions) or not
                        players[playerN].movimientoValido(pos_change[playerN], positions_free)):
                    continue

                players[playerN].move(pos_change[playerN])


                # send pos and recv pos of player 2



                ###


                if [players[playerN].get_posx(), players[playerN].get_posy()] == posW:
                    self.score += 1
                    self.loop()

                players[playerN].draw()

            pointWin.draw()

            # Initialize font and draw title and score text
            pygame.font.init()

            font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

            score_text = 'Puntuacion: {}'.format(self.score)
            score = font.render(score_text, False, Config['colors']['white'])
            title = font.render('LABERINTO', False, Config['colors']['white'])

            title_rect = title.get_rect(
                center=(
                    self.width_able + (self.width_total - self.width_able)/2,
                    100
                )
            )

            score_rect = score.get_rect(
                center=(
                    self.width_able + (self.width_total - self.width_able)/2,
                    200
                )
            )

            self.display.blit(score, score_rect)
            self.display.blit(title, title_rect)

            pygame.display.update()
            clock.tick(Config['game']['fps'])

    def verify_multi(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            sock.send( "verify_multi".encode() )

            time.sleep(1)

            datos = {
                "user_s": self.user["user_s"],
                "pass_s": self.user["pass_s"],
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )

            data = sock.recv(4096).decode()

            return data


    def lists(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            sock.send( "create_pos_multi".encode() )

            time.sleep(1)

            sock.sendall( str(self.num_match).encode() )

            data_all = ""

            while True:
                data = sock.recv(4096).decode()
                if not data:
                    break
                data_all += data

            if data_all != "not_partner":
                from_js = json.loads(data_all)
                return from_js
            else:
                return None

    def get_changes(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            sock.send( "get_change".encode() )

            time.sleep(1)

            datos = {
                "user_s": self.user["user_s"],
                "match": self.num_match
            }

            datos_serial = json.dumps(datos)

            sock.sendall( datos_serial.encode() )

            data_all = ""
            while True:
                data = sock.recv(4096).decode()
                if not data:
                    break
                data_all += data

            from_js = json.loads(data_all)

            return from_js



