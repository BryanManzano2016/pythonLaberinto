import pygame

from src.Config import Config

class Player:
    def __init__(self, display, posP, pos, player="p1"):
        self.x_pos = posP[0]
        self.y_pos = posP[1]
        self.pos_free = pos
        self.display = display
        if player == "p1":
            self.path_img = "src/pykachu.png"
        else:
            self.path_img = "src/duck.png"
        self.picture = pygame.transform.scale(pygame.image.load(self.path_img), (Config['game']['square_size'],
                                                        Config['game']['square_size'],))

    def draw(self):
        self.display.blit(self.picture, (self.x_pos, self.y_pos))

    def verify_pos(self, pos_possible):
        if pos_possible in self.pos_free:
            self.x_pos = pos_possible[0]
            self.y_pos = pos_possible[1]
            return True
        else:
            return False

    def set_position(self, pos_set):
        self.x_pos = pos_set[0]
        self.y_pos = pos_set[1]

    def get_posx(self):
        return self.x_pos

    def get_posy(self):
        return self.y_pos

    def get_pos_xy(self):
        return [self.x_pos, self.y_pos]