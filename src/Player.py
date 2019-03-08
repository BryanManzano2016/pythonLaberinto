import pygame

from src.Config import Config

class Player:
    def __init__(self, display, posP):
        self.x_pos = posP[0]
        self.y_pos = posP[1]
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

    def move(self, change_pos):

        pygame.draw.rect(
            self.display,
            Config['colors']['white'],
            [
                self.x_pos,
                self.y_pos,
                Config['game']['square_size'],
                Config['game']['square_size']
            ]
        )
        self.x_pos += change_pos[0]
        self.y_pos += change_pos[1]

    def movimientoValido(self, change_pos, pos):
        if [self.x_pos + change_pos[0], self.y_pos + change_pos[1]] in pos:
            return True
        else:
            return False

    def get_posx(self):
        return self.x_pos

    def get_posy(self):
        return self.y_pos