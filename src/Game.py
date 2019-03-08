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

    def clean(self, clean_pos):
        pygame.draw.rect(
            self.display,
            Config['colors']['black'],
            [
                clean_pos[0],
                clean_pos[1],
                Config['game']['square_size'],
                Config['game']['square_size']
            ]
        )

    def loop(self):

        clock = pygame.time.Clock()
        self.score = 0

        positions = list() #poner en loop()
        count_sq = 0

        #Posiciones jugables

        positions_free = [ [e, f] for e in range(self.bumper,
                                        self.width_able - self.bumper + self.square_size * 3,
                                        self.square_size)
                          for f in range(self.bumper,
                                        self.height_able - self.bumper + self.square_size * 3,
                                        self.square_size)]

        #Creacion y ubicacion de jugadores y meta
        # dsadd
        posP = random.choice(positions_free)
        positions_free.remove(posP)
        player_1 = Player(self.display, posP)

        posW = random.choice(positions_free)
        positions_free.remove(posW)
        positions.append(posW)
        pointWin = PointWin(self.display, posW)

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

            posObj = random.choice(positions_free)
            positions_free.remove(posObj)
            positions.append(posObj)

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

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    soon_pos = [player_1.get_posx(), player_1.get_posy()]
                    old_pos = soon_pos[:]

                    if event.key == pygame.K_LEFT:
                        soon_pos[0] += -self.square_size
                        if soon_pos in positions_free:
                            player_1.move(soon_pos)
                            self.clean(old_pos)

                    elif event.key == pygame.K_RIGHT:
                        soon_pos[0] += self.square_size
                        if soon_pos not in positions:
                            player_1.move(soon_pos)
                            self.clean(old_pos)

                    elif event.key == pygame.K_UP:
                        soon_pos[1] += -self.square_size
                        if soon_pos not in positions:
                            player_1.move(soon_pos)
                            self.clean(old_pos)

                    elif event.key == pygame.K_DOWN:
                        soon_pos[1] += self.square_size
                        if soon_pos not in positions:
                            player_1.move(soon_pos)
                            self.clean(old_pos)

            # Draw an jugador
            point_rect = pointWin.draw()

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