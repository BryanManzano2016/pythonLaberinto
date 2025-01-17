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

Utiliza los metodos del servidor:  
    Añadir un jugador al inicio
    Verificar que la cuenta exista en la BD y no este actualmente en linea
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

        self.mensaje = ""
        self.textinput = pygame_textinput.TextInput()


        self.menu_main()

    def menu_main(self):

        clock = pygame.time.Clock()
        # Input inicializado

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

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                              (self.height_total / 4) - (self.height_button / 1.5),
                              self.width_button,
                              50,
                              mouse,
                              click,
                              "0")

                data_u = self.textinput.get_text()

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 2) + self.height_button - 100,
                    self.width_button,
                    50,
                    mouse,
                    click,
                    data_u)

            picture_fondo = pygame.transform.scale(pygame.image.load('src/degradado_dark2.jpeg'),
                                             (self.width_total, self.height_total))
            self.display.blit(picture_fondo, (0, 0))

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

            # Rectangulo azul para datos
            pygame.draw.rect(
                self.display,
                Config['colors']['blue'],
                [
                    (self.width_total / 2) - self.width_button,
                    (self.height_total / 2) - 75,
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
                    (self.height_total / 2)  + self.height_button - 100,
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
                    (self.height_total / 2) + self.height_button - 200,
                )
            )

            login_text_rect = login_text.get_rect(
                center=(
                    (self.width_total / 2) + 10,
                    (self.height_total / 2) + self.height_button - 75,
                )
            )

            self.display.blit(invitado_text, invitado_text_rect)
            self.display.blit(datos_text, datos_text_rect)
            self.display.blit(login_text, login_text_rect)

            # Muestra input
            self.display.blit(self.textinput.get_surface(), ( (self.width_total / 2) - (self.width_button / 2),
                (self.height_total / 2) - 65) )

            mensaje_t = '{}'.format(self.mensaje)
            mensaje_text = font.render(mensaje_t, False, Config['colors']['white'])
            mensaje_text_rect = mensaje_text.get_rect(
                center=(
                    (self.width_total / 2) - (self.width_button / 2) + 150,
                    (self.height_total / 2) + self.height_button + 100
                )
            )
            self.display.blit(mensaje_text, mensaje_text_rect)

            self.textinput.update(events)
            pygame.display.update()
            clock.tick(5)


    def buttons_click(self, x, y, wd, hg, mouse, click, data):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            user_pass = data.split(",")

            if click[0] == 1 and data == "0":
                print("----")
                menu_play3.Menu_play(self.display)

            elif click[0] == 1 and data != "":

                if self.verificar_user(data) and len(user_pass) == 2:
                    # Añadir al usuario al servidor mientras dura la conexion
                    user_name = player_dict(data)
                    append_user( user_name["user_s"] )
                    menu_play.Menu_play(self.display, data)

            elif len(user_pass) != 2:
                self.mensaje = "Formato user/pass no valido"

    # Verifica que el player no este en linea y si esta en la BD
    def verificar_user(self, data):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            user = player_dict(data)

            datos = {
                "comando": "verify_user",
                "user_s": user["user_s"],
                "pass_s": user["pass_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall(datos_serial.encode())

            data_all = sock.recv(256).decode()

            if data_all == "ok":
                return True
            else:
                self.mensaje = "No es posible entrar (Usuario ya en linea o datos incorrectos)"
                return False

# Diccionario de datos para login
def player_dict(data_st):
    # Extrae la data del self.user
    user_pass = data_st.split(",")
    user = {
        "user_s" : user_pass[0],
        "pass_s" : user_pass[1]
    }
    return user

# user_st: nombre de usuario a añadir en cadena
def append_user(user_st):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        datos = {
            "comando": "append_user",
            "user_s": user_st
        }

        datos_serial = json.dumps(datos)
        sock.sendall(datos_serial.encode())