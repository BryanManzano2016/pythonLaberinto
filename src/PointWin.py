import random
import pygame

from src.Config import Config


class PointWin:
    def __init__(self, display, pos_x, pos_y):
        self.x_pos = pos_x
        self.y_pos = pos_y
        self.display = display

    # Retorna un rectangulo
    def draw(self):
        return pygame.draw.rect(
            self.display,
            Config['colors']['white'],
            [
                self.x_pos,
                self.y_pos,
                Config['game']['square_size'],
                Config['game']['square_size']
            ]
        )