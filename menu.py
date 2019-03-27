import pygame
from src import pygame_textinput
from src.Config import *
import menu_play
import menu_play3
import socket
import json
import time

'''
Boton invitado: Solo puede jugar partidas only-player 
Boton multijugador: Ingresa user-password y puede jugar only-player o multijugador 
'''

class Menu:

    def __init__(self, display):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']*15
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
        self.square_size = Config['game']['square_size']
        self.height_button = Config['game']['height_button']
        self.width_button = Config['game']['width_button']

        self.menu_main()

    def menu_main(self):

        clock = pygame.time.Clock()
        # Input inicializado
        textinput = pygame_textinput.TextInput()

        while True:

            events = pygame.event.get()

            for event in events:
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:
                    pass
                # Por cada evento alimenta al input
                textinput.update(events)

                # posiciones de mouse y clicks
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                              (self.height_total / 4) - (self.height_button / 1.5),
                              self.width_button,
                              50,
                              mouse,
                              click,
                              "0")

                data_u = textinput.get_text()

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 2) + self.height_button,
                    self.width_button,
                    50,
                    mouse,
                    click,
                    data_u)

            # Fill background and draw game area
            self.display.fill(Config['colors']['green'])

            # Rectangulo blanco para invitado
            pygame.draw.rect(
                self.display,
                Config['colors']['white'],
                [
                    (self.width_total / 2) - self.width_button,
                    (self.height_total / 4) - self.height_button,
                    self.width_button * 2,
                    self.height_button
                ]
            )
            # Rectangulo para boton invitado
            pygame.draw.rect(
                self.display,
                Config['colors']['blue'],
                [
                    (self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 4) - (self.height_button / 1.5),
                    self.width_button,
                    50
                ]
            )

            # Rectangulo blanco para login
            pygame.draw.rect(
                self.display,
                Config['colors']['white'],
                [
                    (self.width_total / 2) - self.width_button,
                    (self.height_total / 2)  - self.height_button,
                    self.width_button * 2,
                    self.height_button * 3
                ]
            )
            # Rectangulo azul para datos
            pygame.draw.rect(
                self.display,
                Config['colors']['blue'],
                [
                    (self.width_total / 2) - self.width_button,
                    (self.height_total / 2) + 25,
                    self.width_button * 2,
                    50
                ]
            )

            # Rectangulo azul para boton login
            pygame.draw.rect(
                self.display,
                Config['colors']['blue'],
                [
                    (self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 2)  + self.height_button,
                    self.width_button,
                    50
                ]
            )

            # Initialize font and draw
            pygame.font.init()
            font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

            # textos
            invitado_text = font.render("INVITADO", False, Config['colors']['white'])
            login_text = font.render('LOGIN', False, Config['colors']['white'])
            datos_text = font.render('DATOS(user,password):', False, Config['colors']['red'])

            invitado_text_rect = invitado_text.get_rect(
                center=(
                    (self.width_total / 2) + 10,
                    (self.height_total / 4) - 40,
                )
            )

            datos_text_rect = login_text.get_rect(
                center=(
                    (self.width_total / 2) - 60,
                    (self.height_total / 2) + self.height_button - 100,
                )
            )

            login_text_rect = login_text.get_rect(
                center=(
                    (self.width_total / 2) + 10,
                    (self.height_total / 2) + self.height_button + 25,
                )
            )

            self.display.blit(invitado_text, invitado_text_rect)
            self.display.blit(datos_text, datos_text_rect)
            self.display.blit(login_text, login_text_rect)

            # Muestra input
            self.display.blit(textinput.get_surface(), ( (self.width_total / 2) - (self.width_button / 2),
                (self.height_total / 2) + 35) )

            pygame.display.update()
            clock.tick(Config['game']['fps'])


    def buttons_click(self, x, y, wd, hg, mouse, click, data):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1 and data == "0":
                menu_play3.Menu_play(self.display)

            elif click[0] == 1 and data != "":
                if verificar_user(data):
                    menu_play.Menu_play(self.display, data)

def verificar_user(data):
    HOST = '127.0.0.1'
    PORT = 60000

    user_pass = str(data).split(",")
    user = {"user_s": user_pass[0], "pass_s": user_pass[1]}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        sock.send( "verify_user".encode() )

        time.sleep(1)

        datos_serial = json.dumps(user)
        sock.sendall(datos_serial.encode())

        data_all = sock.recv(4096).decode()

        print(data_all)

        if data_all == "ok":
            return True
        else:
            return False
