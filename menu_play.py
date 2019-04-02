from src import Config
from src.Game import *
from src.Game2 import *
from src.Game3 import *

'''
-Se observaran los botones de play y multijugador

Utiliza los metodos del servidor:  
    Borrar un usuario del servidor, en caso de que salga
    Borrar una partida en caso de que la cree y no reciba respuestas
'''

HOST = '192.168.100.133'
PORT = 60000

class Menu_play:

    def __init__(self, display, data):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']*15
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
        self.square_size = Config['game']['square_size']
        self.height_button = Config['game']['height_button']
        self.width_button = Config['game']['width_button']

        self.data = data
        self.user = self.player_dict()

        self.num_match = None

        self.mensaje = ""

        self.menu_main()

    def menu_main(self):

        clock = pygame.time.Clock()

        while True:

            events = pygame.event.get()

            for event in events:
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    self.delete_user()
                    self.delete_match_2()
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:
                    pass

                # posiciones de mouse y clicks
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()

                self.buttons_click((self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 2) - self.height_button + 20,
                    self.width_button,
                    50,
                    mouse,
                    click)

                self.buttons_click_i((self.width_total / 2) - (self.width_button / 2),
                              (self.height_total / 4) - (self.height_button / 1.5),
                              self.width_button,
                              50,
                              mouse,
                              click)

            picture_fondo = pygame.transform.scale(pygame.image.load('src/degradado_dark2.jpeg'),
                                             (self.width_total, self.height_total))
            self.display.blit(picture_fondo, (0, 0))

            # Rectangulo para boton play
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

            # Initialize font and draw
            pygame.font.init()
            font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

            # textos
            play_text = font.render("PLAY", False, Config['colors']['white'])

            play_text_rect = play_text.get_rect(
                center=(
                    (self.width_total / 2) + 10,
                    (self.height_total / 4) - 40,
                )
            )

            # Rectangulo azul para boton multiplayer
            pygame.draw.rect(
                self.display,
                Config['colors']['blue'],
                [
                    (self.width_total / 2) - (self.width_button / 2),
                    (self.height_total / 2) - self.height_button + 20,
                    self.width_button,
                    50
                ]
            )

            multiplayer_text = font.render('MULTIPLAYER', False, Config['colors']['white'])

            multiplayer_text_rect = multiplayer_text.get_rect(
                center=(
                    (self.width_total / 2) + 15,
                    (self.height_total / 2) - self.height_button + 40
                )
            )

            mensaje_t = '{}'.format(self.mensaje)
            mensaje_text = font.render(mensaje_t, False, Config['colors']['white'])
            mensaje_text_rect = mensaje_text.get_rect(
                center=(
                    (self.width_total / 2) - (self.width_button / 2) + 150,
                    (self.height_total / 2) + self.height_button + 100
                )
            )

            self.display.blit(mensaje_text, mensaje_text_rect)
            self.display.blit(multiplayer_text, multiplayer_text_rect)
            self.display.blit(play_text, play_text_rect)

            pygame.display.update()
            clock.tick(5)


    def buttons_click(self, x, y, wd, hg, mouse, click):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1:

                # Intenta conectar 2 jugadores
                self.connect_player()
                # Si la partida no tiene 2 jugadores, se elimina la partida creada y la pantalla se refresca
                self.verify_multi_out()

                Game(self.display, self.user, self.num_match)

    def buttons_click_i(self, x, y, wd, hg, mouse, click):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1:
                # Solo borra partida no usuario en linea
                self.delete_match_2()
                Game2(self.display, self.user)

    def player_dict(self):
        # Extrae la data del self.user
        user_pass = str(self.data).split(",")
        user = {
            "user_s" : user_pass[0],
            "pass_s" : user_pass[1]
        }
        return user

    # Envia peticion para jugar multiplayer, esto crea una partida o actualiza un jugador nulo de una existen
    def connect_player(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            datos = {
                "comando": "connect_players",
                "user_s": self.user["user_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall(datos_serial.encode())

    # Retorna el nro de partida, -1 si no existe
    def verify_multi(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            # Envia un objeto serializado atraves de sockets
            datos = {
                "comando": "verify_multi",
                "user_s": self.user["user_s"],
                "pass_s": self.user["pass_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )

            # Recibe un objeto serializado atraves de sockets
            data = json.loads( sock.recv(256).decode() )

            return data["match"]

    # Cada 3 segundos ejecuta verify_multi, si se pasa de 60 segundos cierra el juego
    def verify_multi_out(self):

        count_seconds = 0
        self.num_match = self.verify_multi()
        # -1 significa que no llega oponente, no hay 2 jugadores en la partida
        while self.num_match == -1:
            time.sleep(1)
            self.num_match = self.verify_multi()
            count_seconds += 1
            #Reinicia la pantalla y elimina la partida que creo
            if count_seconds > 60:
                self.mensaje = "No hubo rival"
                self.menu_main()
                self.delete_match_2()

    # Borra el usuario en linea
    def delete_user(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            user_name = self.player_dict()

            datos = {
                "comando": "delete_user",
                "user_s": user_name["user_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall(datos_serial.encode())

    # Borra la partida activa en el servidor
    def delete_match_2(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            user_name = self.player_dict()

            datos = {
                "comando": "delete_match2",
                "user_s": user_name["user_s"]
            }

            datos_serial = json.dumps(datos)
            sock.sendall( datos_serial.encode() )