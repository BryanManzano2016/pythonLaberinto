import pygame
import random

from src.Config import Config

class Player:
    def __init__(self, display, pos_x, pos_y):
        self.x_pos = pos_x
        self.y_pos = pos_y
        self.display = display

    def draw(self):
        return pygame.draw.rect(
            self.display,
            Config['colors']['blue'],
            [
                self.x_pos,
                self.y_pos,
                Config['game']['square_size'],
                Config['game']['square_size']
            ]
        )

    def move(self, x_change, y_change, pos_free):
        if [self.x_pos] not in pos_free:
            pygame.draw.rect(
                self.display,
                Config['colors']['black'],
                [
                    self.x_pos,
                    self.y_pos,
                    Config['game']['square_size'],
                    Config['game']['square_size']
                ]
            )
            self.x_pos += x_change
            self.y_pos += y_change


