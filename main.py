import pygame
from src import Config
from src.Game import *
import menu

def main():
    #Dimensiones de la pantalla
    display = pygame.display.set_mode((
        Config['game']['width'],
        Config['game']['height']
    ))
    #Titulo
    pygame.display.set_caption(Config['game']['caption'])

    menus = menu.Menu(display)

if __name__ == '__main__':
    main()