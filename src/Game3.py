import pygame
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config
import socket
import json

# Modo invitado

class Game3:

    def __init__(self, display):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']*15
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
        self.square_size = Config['game']['square_size']

        self.score = 0
        self.segundo = 0

        self.loop()

    def loop(self):

        clock = pygame.time.Clock()

        positions_free, positions, pos_m = lists()

        #Creacion y ubicacion de jugadores y meta
        posP = pos_m[0]
        player_1 = Player(self.display, posP)

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

            # Se puede añadir mas listas en pos_change para mas jugadores
            pos_change = [[0, 0]]

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        pos_change[0][0] += -self.square_size
                        pos_change[0][1] = 0

                        if (players[0].movimientoValido(pos_change[0], positions) or not
                        players[0].movimientoValido(pos_change[0], positions_free)):
                            pos_change[0] = [0, 0]

                    elif event.key == pygame.K_RIGHT:
                        pos_change[0][0] += self.square_size
                        pos_change[0][1] = 0

                        if (players[0].movimientoValido(pos_change[0], positions) or not
                        players[0].movimientoValido(pos_change[0], positions_free)):
                            pos_change[0] = [0, 0]

                    elif event.key == pygame.K_UP:
                        pos_change[0][0] = 0
                        pos_change[0][1] += -self.square_size

                        if (players[0].movimientoValido(pos_change[0], positions) or not
                        players[0].movimientoValido(pos_change[0], positions_free)):
                            pos_change[0] = [0, 0]

                    elif event.key == pygame.K_DOWN:
                        pos_change[0][0] = 0
                        pos_change[0][1] += self.square_size

                        if (players[0].movimientoValido(pos_change[0], positions) or not
                        players[0].movimientoValido(pos_change[0], positions_free)):
                            pos_change[0] = [0, 0]

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

            # range tiene 1 porque solo hay 1 jugador en players
            for playerN in range(1):

                if (players[playerN].movimientoValido(pos_change[playerN], positions) or not
                        players[playerN].movimientoValido(pos_change[playerN], positions_free)):
                    continue

                players[playerN].move(pos_change[playerN])

                if [players[playerN].get_posx(), players[playerN].get_posy()] == posW:
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

def lists():
    HOST = '192.168.100.133'
    PORT = 60000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        sock.sendall( "create_pos".encode() )

        data_all = ""
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            data_all += data

        from_js = json.loads(data_all)
    sock.close()
    return from_js["positions_free"], from_js["positions"], from_js["pos"]

