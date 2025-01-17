import pygame
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config
import socket
import json

# Modo multijugador
HOST = '192.168.100.133'
PORT = 60000

'''
num_match: nro de la partida en el servidor
nro_player: es igual a P1 p P2 segun llegue 1ero la solicitud 
nro_oponent: es igual a P1 p P2 segun llegue 1ero la solicitud
user_player: nombre de usuario de jugador local
user_oponent: nombre de usuario de oponente
'''
class Game:

    def __init__(self, display, user_g, match):
        # Datos de juego
        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size'] * 10
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 2
        self.square_size = Config['game']['square_size']

        self.user = user_g
        self.num_match = match
        self.nro_player = None
        self.nro_oponent = None
        self.user_player = None
        self.user_oponent = None

        # Verifico el numero de partida durante un lapso de tiempo
        self.loop()

    def loop(self):

        clock = pygame.time.Clock()

        # Extraccion de posiciones iniciales
        posit = self.lists()
        positions_free = posit["positions_m"]["positions_free"]
        positions = posit["positions_m"]["positions"]
        posP = list()
        posP2 = list()

        # Define quien es 1er jugador y 2do jugador
        if self.user["user_s"] == posit["p1"]:
            posP = posit["positions_m"]["pos"][0]
            posP2 = posit["positions_m"]["pos"][1]
            self.nro_player = "p1"
            self.nro_oponent = "p2"
            self.user_player = posit["p1"]
            self.user_oponent = posit["p2"]
        elif self.user["user_s"] == posit["p2"]:
            posP = posit["positions_m"]["pos"][1]
            posP2 = posit["positions_m"]["pos"][0]
            self.nro_player = "p2"
            self.nro_oponent = "p1"
            self.user_player = posit["p2"]
            self.user_oponent = posit["p1"]

        #Creacion y ubicacion de jugadores y meta
        player_1 = Player(self.display, posP, positions_free, self.nro_player)
        player_2 = Player(self.display, posP2, positions_free, self.nro_oponent)

        posW = posit["positions_m"]["pos"][2]
        pointWin = PointWin(self.display, posW)

        # Añade a una lista los jugadores para posterior iteracion
        players = list()
        players.append(player_1)
        players.append(player_2)

        while True:

            # Obtener posicion del rival
            score_local = 0
            score_oponent = 0
            changes = self.get_changes()

            if self.nro_player == "p1":
                players[0].set_position(changes["change_p1"])
                players[1].set_position(changes["change_p2"])
                score_local = changes["p1_points"]
                score_oponent = changes["p2_points"]
            else:
                players[0].set_position(changes["change_p2"])
                players[1].set_position(changes["change_p1"])
                score_local = changes["p2_points"]
                score_oponent = changes["p1_points"]

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    self.delete_match()
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[0] += -self.square_size

                        # Con una funcion de la clase player se verifica si es valido el movimiento
                        if players[0].verify_pos(pos_player_pos):
                            # Si lo es, envia la posicion al servidor
                            self.update_change(players[0].get_pos_xy())

                    elif event.key == pygame.K_RIGHT:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[0] += self.square_size

                        if players[0].verify_pos(pos_player_pos):
                            self.update_change(players[0].get_pos_xy())

                    elif event.key == pygame.K_UP:

                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[1] += -self.square_size

                        if players[0].verify_pos(pos_player_pos):
                            self.update_change(players[0].get_pos_xy())
                    elif event.key == pygame.K_DOWN:
                        pos_player_pos = players[0].get_pos_xy()
                        pos_player_pos[1] += self.square_size

                        if players[0].verify_pos(pos_player_pos):
                            self.update_change(players[0].get_pos_xy())

            # Fondos e imagenes
            picture_fondo = pygame.transform.scale(pygame.image.load('src/degradado_dark2.jpeg'),
                                             (self.width_total, self.height_total))
            self.display.blit(picture_fondo, (0, 0))

            picture_fondo_play = pygame.transform.scale(pygame.image.load('src/degradado.png'),
                                             (self.width_able, self.height_able))
            self.display.blit(picture_fondo_play, (self.square_size, self.square_size))
            # Dibuja los cuadritos del laberinto
            picture = pygame.transform.scale(pygame.image.load('src/block_red.png'),
                                             (self.square_size, self.square_size))
            for x in positions:
                self.display.blit(picture, (x[0], x[1]))

            # Dibuja los jugadores
            players[0].draw()
            players[1].draw()
            pointWin.draw()

            # Initialize font and draw title and score text
            pygame.font.init()

            font = pygame.font.SysFont(pygame.font.get_default_font(), 35)

            title = font.render('LABERINTO', False, Config['colors']['white'])
            title_rect = title.get_rect(
                center=(
                    self.width_able + (self.width_total - self.width_able) / 2,
                    100
                )
            )

            score_text = 'Local: {}'.format(score_local)
            score_1 = font.render(score_text, False, Config['colors']['white'])
            score_text_rect = score_1.get_rect(
                center=(
                    self.width_able + (self.width_total - self.width_able) / 2,
                    200
                )
            )

            score_text_2 = 'Oponent: {}'.format(score_oponent)
            score_2 = font.render(score_text_2, False, Config['colors']['white'])
            score_text_rect_2 = score_2.get_rect(
                center=(
                    self.width_able + (self.width_total - self.width_able) / 2,
                    300
                )
            )

            self.display.blit(score_1, score_text_rect)
            self.display.blit(score_2, score_text_rect_2)
            self.display.blit(title, title_rect)

            pygame.display.update()
            clock.tick(Config['game']['fps'])

    # Data de la partida
    def lists(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "create_posMulti",
                "user_s": self.user["user_s"],
                "match": self.num_match
            }

            sock.sendall( (json.dumps(datos)).encode() )

            data_all = ""
            while True:
                # 4096 es debido a que recibe por partes data de gran tamaño por partes
                data = sock.recv(4096).decode()
                if not data:
                    break
                data_all += data
            # Si hay rival, deserealiza la informacion
            if data_all != "not_partner":
                from_js = json.loads(data_all)
                return from_js
            else:
                return None

    # Envia usuario y nro de partida para obtener cambio de rival
    def get_changes(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "get_change",
                "nro_player": self.nro_player,
                "match": self.num_match
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )

            data = sock.recv(256).decode()

            # Si se salio del juego el oponente
            if data == "not_match":
                exit()
            # Si existio un reinicio por exceso de tiempo
            elif data == "reboot":
                self.loop()
            else:
                data_all = json.loads(data)
                return data_all

    # Modifica la posicion de jugador local
    def update_change(self, change):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "update_change",
                "nro_player": self.nro_player,
                "match": self.num_match,
                "change": [change[0], change[1]]
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )

    # Borra la partida activa en el servidor
    def delete_match(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "delete_match",
                "match": self.num_match
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )
