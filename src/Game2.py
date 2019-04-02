import pygame
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config
import socket
import json
import time

# Modo UP de un solo jugador
HOST = '192.168.100.133'
PORT = 60000

class Game2:

    def __init__(self, display, user_g):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size'] * 10
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 2
        self.square_size = Config['game']['square_size']

        self.score = 0
        self.segundo = 0

        self.user = user_g

        self.loop()

    def loop(self):

        clock = pygame.time.Clock()

        positions_free, positions, pos_m = lists()

        #Creacion y ubicacion de jugadores y meta
        posP = pos_m[0]
        player_1 = Player(self.display, posP, positions_free)

        # Se puede añadir mas jugadores en players
        players = list()
        players.append(player_1)

        posW = pos_m[1]
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
            if self.segundo == 45:
                self.segundo = 0
                self.loop()

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    self.delete_user()
                    self.send_record()
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[0] += -self.square_size

                        players[0].verify_pos(pos_player_pos)

                    elif event.key == pygame.K_RIGHT:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[0] += self.square_size

                        players[0].verify_pos(pos_player_pos)

                    elif event.key == pygame.K_UP:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[1] += -self.square_size

                        players[0].verify_pos(pos_player_pos)

                    elif event.key == pygame.K_DOWN:
                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[1] += self.square_size

                        players[0].verify_pos(pos_player_pos)

            # Fondos e imagenes -------------------------------------------------------------

            picture_fondo = pygame.transform.scale(pygame.image.load('src/degradado_dark2.jpeg'),
                                             (self.width_total, self.height_total))
            self.display.blit(picture_fondo, (0, 0))

            picture_fondo_play = pygame.transform.scale(pygame.image.load('src/degradado.png'),
                                             (self.width_able, self.height_able))
            self.display.blit(picture_fondo_play, (self.square_size, self.square_size))

            picture = pygame.transform.scale(pygame.image.load('src/block_red.png'),
                                             (self.square_size, self.square_size))
            for x in positions:
                self.display.blit(picture, (x[0], x[1]))

            # -------------------------------------------------------------------------------
            # range tiene 1 porque solo hay 1 jugador en players
            for playerN in range(1):

                if players[playerN].get_pos_xy() == posW:
                    self.score += 1
                    self.segundo = 0
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

    # Envia puntuacion al momento de cerrar el juego
    def send_record(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "send_points",
                "user_s": self.user["user_s"],
                "pass_s": self.user["pass_s"],
                "record": self.score
            }

            datos_serial = json.dumps(datos)
            sock.sendall(datos_serial.encode())

    def delete_user(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "delete_user",
                "user_s": self.user["user_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall(datos_serial.encode())

def lists():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        datos = {
            "comando": "create_pos",
        }

        datos_serial = json.dumps(datos)
        sock.sendall(datos_serial.encode())

        data_all = ""
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            data_all += data
        from_js = json.loads(data_all)

    return from_js["positions_free"], from_js["positions"], from_js["pos"]
