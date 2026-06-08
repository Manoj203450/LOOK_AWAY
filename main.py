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

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Look Away")
clock = pygame.time.Clock()


def play_level(level_func, screen, clock, **kwargs):
    first_run = True
    while True:
        if first_run:
            kwargs.pop("restart_music", None)
            result = level_func(screen, clock, **kwargs)
        else:
            kwargs.pop("restart_music", None)
            result = level_func(screen, clock,
                                restart_music=True, **kwargs)
        first_run = False

        if result == "menu":
            stop_music()
            return "menu"
        if result is not None:
            return result

def run_game_from(level, gives_wrench, screen, clock):
    from systems.potion import PotionInventory
    potion_inv = PotionInventory()

    if level <= 1:
        play_music("assets/audio/audio_1.ogg",
                   loop=True, volume=0.3)
        result = play_level(run_level1, screen, clock,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level2":
            return
        level = 2
        music_already_playing = True
    else:
        music_already_playing = False

    if level <= 2:
        if not music_already_playing:
            # Coming from level select — start music fresh
            play_music("assets/audio/audio_1.ogg",
                       loop=True, volume=0.3)
        result = play_level(run_level2, screen, clock,
                            potion_inv=potion_inv,
                            restart_music=False)  # ← always False here
        if result == "menu":
            return
        if result != "level3":
            return
        level = 3

    if level <= 3:
        stop_music()
        play_music("assets/audio/audio_2.ogg",
                   loop=True, volume=0.3)
        result = play_level(run_level3, screen, clock,
                            start_with_wrench=True,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level4":
            return
        level = 4

    if level <= 4:
        stop_music()
        play_music("assets/audio/moon_theme.ogg", loop=True, volume=0.4)
        result = play_level(run_level4, screen, clock,
                            start_with_wrench=True,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result not in ("level5", "level6"):
            return
        level = 5

    if level <= 5:
        result = play_level(run_level5, screen, clock,
                            start_with_wrench=True,
                            potion_inv=potion_inv)
        if result == "menu":
            return
        if result != "level6":
            return
        level = 6

    # level_6 is wired in directly for now so it can be tested standalone
    if level <= 6:
        stop_music()
        result = play_level(run_level6, screen, clock,
                            potion_inv=potion_inv)
        if result == "menu":
            return

# MAIN LOOP
while True:
    choice = run_menu(screen, clock)

    if choice == "START NEW GAME":
        stop_music()
        run_intro(screen, clock)
        run_game_from(1, False, screen, clock)
        stop_music()

    elif choice == "LOAD GAME":
        selection = run_level_select(screen, clock)
        if selection is not None:
            stop_music()
            run_game_from(
                selection["level"],
                selection["gives_wrench"],
                screen, clock
            )
            stop_music()

    elif choice == "CREDITS":
        run_credits(screen, clock)

    elif choice == "EXIT":
        pygame.quit()
        sys.exit()