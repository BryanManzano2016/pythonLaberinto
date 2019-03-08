import pygame
import random
from src.Player import Player
from src.PointWin import PointWin
from src.Config import Config

class Game:
    def __init__(self, display):

        self.display = display
        self.width_total = Config['game']['width']
        self.width_able = Config['game']['width'] - Config['game']['bumper_size']*15
        self.height_total = Config['game']['height']
        self.height_able = Config['game']['height'] - Config['game']['bumper_size'] * 1
        self.square_size = Config['game']['square_size']

        self.score = 0

    def loop(self):

        clock = pygame.time.Clock()

        positions = list() #poner en loop()
        count_sq = 0

        #Posiciones jugables

        positions_free = [ [e, f] for e in range(self.square_size,
                                        self.width_able + self.square_size,
                                        self.square_size)
                          for f in range(self.square_size,
                                        self.height_able + self.square_size,
                                        self.square_size)]

        #Creacion y ubicacion de jugadores y meta
        posP = random.choice(positions_free)
        player_1 = Player(self.display, posP)

        posW = random.choice(positions_free)
        pointWin = PointWin(self.display, posW)

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

        while count_sq < Config['game']['number_squares']:

            posObj = random.choice(positions_free)
            positions_free.remove(posObj)
            positions.append(posObj)

            count_sq += 1

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

        while True:

            pos_change = [0, 0]

            for event in pygame.event.get():
                # Si se sale del programa
                if event.type == pygame.QUIT:
                    exit()

                # Si se presiona una tecla
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        pos_change[0] += -self.square_size
                        pos_change[1] = 0

                    elif event.key == pygame.K_RIGHT:
                        pos_change[0] += self.square_size
                        pos_change[1] = 0

                    elif event.key == pygame.K_UP:
                        pos_change[0] = 0
                        pos_change[1] += -self.square_size

                    elif event.key == pygame.K_DOWN:
                        pos_change[0] = 0
                        pos_change[1] += self.square_size

            if (player_1.movimientoValido(pos_change, positions) or not
                    player_1.movimientoValido(pos_change, positions_free)):
                continue

            player_1.move(pos_change)

            player_rect = player_1.draw()
            point_rect = pointWin.draw()
                # Detect collision with point of wein
            if player_rect.colliderect(point_rect):
                self.loop()
                self.score += 1

            '''
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
            '''
            pygame.display.update()
            clock.tick(Config['game']['fps'])