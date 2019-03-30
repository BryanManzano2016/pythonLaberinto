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

HOST = '192.168.100.133'
PORT = 60000

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

                # posiciones de mouse y clicks
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()

                data_u = textinput.get_text()

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                              (self.height_total / 4) - (self.height_button / 1.5),
                              self.width_button,
                              50,
                              mouse,
                              click,
                              "0")

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

            textinput.update(events)

            pygame.display.update()
            clock.tick(5)


    def buttons_click(self, x, y, wd, hg, mouse, click, data):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1 and data == "0":
                menu_play3.Menu_play(self.display)

            elif click[0] == 1 and data != "":
                if verificar_user(data):
                    # Añadir al usuario al servidor mientras dura la conexion
                    time.sleep(1)
                    user_name = player_dict(data)
                    append_user( user_name["user_s"] )
                    time.sleep(1)
                    menu_play.Menu_play(self.display, data)

def player_dict(data_st):
    # Extrae la data del self.user
    user_pass = data_st.split(",")
    user = {
        "user_s" : user_pass[0],
        "pass_s" : user_pass[1]
    }
    return user

def verificar_user(data):

    user = player_dict(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        sock.send( "verify_user".encode() )

        time.sleep(1)

        datos_serial = json.dumps(user)
        sock.sendall(datos_serial.encode())

        data_all = sock.recv(256).decode()

        if data_all == "ok":
            return True
        else:
            return False

# user_st: nombre de usuario a añadir en cadena
def append_user(user_st):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        sock.send( "append_user".encode() )

        time.sleep(1)

        sock.sendall( user_st.encode() )