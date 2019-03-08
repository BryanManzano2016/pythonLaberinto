import pygame

from src.Config import Config


class PointWin:
    def __init__(self, display, posW):
        self.x_pos = posW[0]
        self.y_pos = posW[1]
        self.display = display

    # Retorna un rectangulo
    def draw(self):
        return pygame.draw.rect(
            self.display,
            Config['colors']['orange'],
            [
                self.x_pos,
                self.y_pos,
                Config['game']['square_size'],
                Config['game']['square_size']
            ]
        )