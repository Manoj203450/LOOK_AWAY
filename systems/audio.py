import pygame


def init_audio():
    pygame.mixer.init()


def play_music(path, loop=True, volume=0.5):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        # -1 = loop forever, 0 = play once
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception as e:
        print(f"Audio error: {e}")
        pass


def stop_music():
    pygame.mixer.music.stop()


def fade_out_music(ms=1000):
    pygame.mixer.music.fadeout(ms)


def play_sfx(path, volume=0.7):
    try:
        sfx = pygame.mixer.Sound(path)
        sfx.set_volume(volume)
        sfx.play()
    except Exception as e:
        print(f"SFX error: {e}")
        pass