import pygame
from src import Config
from src.Game import *
from src.Game2 import *
from src.Game3 import *

'''
-Se observaran los botones de play y multijugador
'''

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

        self.menu_main()

    def menu_main(self):

        clock = pygame.time.Clock()

        while True:

            events = pygame.event.get()

            for event in events:
                # Si se sale del programa
                if event.type == pygame.QUIT:
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

            # Fill background and draw game area
            self.display.fill(Config['colors']['green'])

            # Rectangulo blanco para play
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

            # Rectangulo blanco para multiplayer
            pygame.draw.rect(
                self.display,
                Config['colors']['white'],
                [
                    (self.width_total / 2) - self.width_button,
                    (self.height_total / 2) - self.height_button,
                    self.width_button * 2,
                    self.height_button
                ]
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

            self.display.blit(multiplayer_text, multiplayer_text_rect)

            self.display.blit(play_text, play_text_rect)

            pygame.display.update()
            clock.tick(Config['game']['fps'])


    def buttons_click(self, x, y, wd, hg, mouse, click):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1:
                game = Game(self.display, self.data)

    def buttons_click_i(self, x, y, wd, hg, mouse, click):

        if x + wd > mouse[0] > x and y + hg > mouse[1] > y:

            if click[0] == 1:
                game = Game2(self.display, self.data)
