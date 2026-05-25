import pygame
import sys
from menu import run_menu
from intro import run_intro
from level_1 import run_level1
from level_2 import run_level2
from level_3 import run_level3
from level_select import run_level_select
from credits import run_credits


pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Look Away")
clock = pygame.time.Clock()


def play_level(level_func, screen, clock, **kwargs):
    while True:
        result = level_func(screen, clock, **kwargs)
        if result == "menu":
            return "menu"
        if result is not None:
            return result


def run_game_from(level, gives_wrench, screen, clock):
    from systems.potion import PotionInventory
    potion_inv = PotionInventory()

    if level <= 1:
        result = play_level(run_level1, screen, clock,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level2":
            return
        level = 2

    if level <= 2:
        result = play_level(run_level2, screen, clock,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level3":
            return
        level = 3

    if level <= 3:
        result = play_level(run_level3, screen, clock,
                            start_with_wrench=True,
                            potion_inv=potion_inv)
        if result == "menu":
            return


# MAIN LOOP
while True:
    choice = run_menu(screen, clock)

    if choice == "START NEW GAME":
        run_intro(screen, clock)
        run_game_from(1, False, screen, clock)

    elif choice == "LOAD GAME":
        selection = run_level_select(screen, clock)
        if selection is not None:
            run_game_from(
                selection["level"],
                selection["gives_wrench"],
                screen, clock
            )

    elif choice == "CREDITS":
        run_credits(screen, clock)

    elif choice == "EXIT":
        pygame.quit()
        sys.exit()