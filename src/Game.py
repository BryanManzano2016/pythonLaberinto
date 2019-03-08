import pygame
import random
#from time import sleep
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config

class Game:
    def __init__(self, display):

        self.display = display
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size']
        self.width_total = Config['game']['width']
        self.height_total = Config['game']['height']
        self.bumper = Config['game']['bumper_size']
        self.square_size = Config['game']['square_size']

        self.score = 0

    def loop(self):

        clock = pygame.time.Clock()
        self.score = 0

        positions = list() #poner en loop()
        count_sq = 0

        #Posiciones jugables
        posx_square = [e for e in range(self.bumper,
                                        self.width_able - self.bumper + self.square_size * 3,
                                        self.square_size)]
        posy_square = [e for e in range(self.bumper,
                                        self.height_able - self.bumper + self.square_size * 3,
                                        self.square_size)]

        #Creacion y ubicacion de jugadores y meta
        posxP_random = random.choice(posx_square)
        posyP_random = random.choice(posy_square)
        positions.append([posxP_random, posyP_random])
        player_1 = Player(self.display, posxP_random, posyP_random)

        posxW_random = random.choice(posx_square)
        posyW_random = random.choice(posy_square)
        positions.append([posxW_random, posyW_random])
        pointWin = PointWin(self.display, posxW_random, posyW_random)

        x_change = 0
        y_change = 0

        # Fill background and draw game area
        self.display.fill(Config['colors']['green'])

        # Rectangulo negro de juego
        pygame.draw.rect(
            self.display,
            Config['colors']['black'],
            [
                self.bumper,
                self.bumper,
                self.width_able - self.bumper,
                self.height_able - self.bumper
            ]
        )

        while count_sq < Config['game']['number_squares']:

            posx_random = random.choice(posx_square)
            posy_random = random.choice(posy_square)

            if [posx_random, posy_random] not in positions:
                positions.append([posx_random, posy_random])
                count_sq += 1

        for x in positions:
            pygame.draw.rect(
                self.display,
                Config['colors']['yellow'],
                [
                    x[0],
                    x[1],
                    self.square_size,
                    self.square_size
                ]
            )

        while True:
            #sleep(1)
            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x_change = -self.square_size
                        y_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x_change = self.square_size
                        y_change = 0
                    elif event.key == pygame.K_UP:
                        x_change = 0
                        y_change = -self.square_size
                    elif event.key == pygame.K_DOWN:
                        x_change = 0
                        y_change = self.square_size

            # Draw an jugador
            point_rect = pointWin.draw()

            player_1.move(x_change, y_change, positions)
            player_rect = player_1.draw()

            # Detect collision with point of wein
            if point_rect.colliderect(player_rect):
                self.loop()

            # Initialize font and draw title and score text
            pygame.font.init()
            font = pygame.font.Font('./assets/Now-Regular.otf', 28)

            score_text = 'Puntuacion: {}'.format(self.score)
            score = font.render(score_text, True, Config['colors']['white'])
            title = font.render('LABERINTO', True, Config['colors']['white'])

            title_rect = title.get_rect(
                center=(
                    self.width_able / 2,
                    self.bumper / 2
                )
            )

            score_rect = score.get_rect(
                center=(
                    self.width_able / 2,
                    self.height_able + (self.bumper / 2)
                )
            )

            self.display.blit(score, score_rect)
            self.display.blit(title, title_rect)

            pygame.display.update()
            clock.tick(Config['game']['fps'])