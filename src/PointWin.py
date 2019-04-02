import pygame

from src.Config import Config


class PointWin:
    def __init__(self, display, posW):
        self.x_pos = posW[0]
        self.y_pos = posW[1]
        self.display = display
        self.picture = pygame.transform.scale(pygame.image.load("src/star.png"), (Config['game']['square_size'],
                                                        Config['game']['square_size'],))

    # Retorna un rectangulo
    def draw(self):
        self.display.blit(self.picture, (self.x_pos, self.y_pos))
