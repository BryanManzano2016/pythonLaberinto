import pygame
from src import Config
from src.Game import *

def main():
    #Dimensiones de la pantalla
    display = pygame.display.set_mode((
        Config['game']['width'],
        Config['game']['height']
    ))
    #Tituto
    pygame.display.set_caption(Config['game']['caption'])

    game = Game(display)

if __name__ == '__main__':
    main()