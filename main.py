import pygame
import sys
from menu import run_menu
from intro import run_intro
from level_1 import run_level1
from level_2 import run_level2
from level_3 import run_level3
from level_4 import run_level4
from level_5 import run_level5
from level_6 import run_level6
from level_select import run_level_select
from credits import run_credits
from systems.audio import play_music, stop_music, play_sfx
from settings_screen import run_settings
from systems.settings_manager import settings

pygame.init()
pygame.mixer.init()

# Fixed windowed ratio size
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)

pygame.display.set_caption("Look Away")
clock = pygame.time.Clock() # 60 fps all levels


def play_level(level_func, screen, clock, **kwargs):    # **kwargs is a wrapper for extra passed arguments
    first_run = True
    start_health = kwargs.pop("start_health", 100)
    while True:
        if first_run:
            kwargs.pop("restart_music", None)
            result = level_func(screen, clock, **kwargs)
        else:
            kwargs.pop("restart_music", None)
            result = level_func(screen, clock, restart_music=True, **kwargs)
        first_run = False

        if isinstance(result, tuple):
            level_result, exit_health = result
        else:
            level_result = result
            exit_health = 100

        if level_result == "menu":
            stop_music()
            return "menu", 100
        if level_result is not None:
            return level_result, exit_health

def run_game_from(level, gives_wrench, screen, clock):
    from systems.potion import PotionInventory
    potion_inv = PotionInventory()
    carry_health = 100

    if level <= 1:
        play_music("assets/audio/lvl1.ogg", loop=True, volume=0.3)
        result, carry_health = play_level(run_level1, screen, clock,
                                          potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level2":
            return
        level = 2

    if level <= 2:
        play_music("assets/audio/audio_1.ogg", loop=True, volume=0.3)
        result, carry_health = play_level(run_level2, screen, clock,
                                          potion_inv=potion_inv,
                                          restart_music=False,
                                          start_health=carry_health)
        if result == "menu":
            return
        if result != "level3":
            return
        level = 3

    if level <= 3:
        stop_music()
        play_music("assets/audio/audio_2.ogg", loop=True, volume=0.3)
        result, carry_health = play_level(run_level3, screen, clock,
                                          start_with_wrench=True,
                                          potion_inv=potion_inv,
                                          start_health=carry_health)
        if result == "menu":
            return
        if result != "level4":
            return
        level = 4

    if level <= 4:
        stop_music()
        play_music("assets/audio/moon_theme.ogg", loop=True, volume=0.4)
        result, carry_health = play_level(run_level4, screen, clock,
                                          start_with_wrench=True,
                                          potion_inv=potion_inv,
                                          start_health=carry_health)
        if result == "menu":
            return
        if result not in ("level5", "level6"):
            return
        level = 5

    if level <= 5:
        result, carry_health = play_level(run_level5, screen, clock,
                                          start_with_wrench=True,
                                          potion_inv=potion_inv,
                                          start_health=carry_health)
        if result == "menu":
            return
        if result != "level6":
            return
        level = 6

    if level <= 6:
        stop_music()
        result, carry_health = play_level(run_level6, screen, clock,
                                          start_with_wrench=True,
                                          potion_inv=potion_inv,
                                          start_health=carry_health)
        if result == "menu":
            return

# --
# MAIN LOOP
# --
while True:
    choice = run_menu(screen, clock)

    if choice == "START NEW GAME":
        stop_music()
        run_intro(screen, clock)
        run_game_from(1, False, screen, clock)
        stop_music()

    elif choice == "SELECT LEVEL":
        selection = run_level_select(screen, clock)
        if selection is not None:
            stop_music()
            run_game_from(
                selection["level"],
                selection["gives_wrench"],
                screen, clock
            )
            stop_music()

    elif choice == "SETTINGS":
        run_settings(screen, clock)
        screen = pygame.display.get_surface()

    elif choice == "CREDITS":
        run_credits(screen, clock)

    elif choice == "EXIT":
        pygame.quit()
        sys.exit()