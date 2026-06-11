import pygame


def init_audio():
    pygame.mixer.init()


def play_music(path, loop=True, volume=0.5):
    try:
        try:
            from systems.settings_manager import settings
            volume = settings.get("music_volume", volume)
        except Exception:
            pass
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
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
        try:
            from systems.settings_manager import settings
            volume = volume * settings.get("sfx_volume", 1.0)
        except Exception:
            pass
        sfx = pygame.mixer.Sound(path)
        sfx.set_volume(volume)
        sfx.play()
    except Exception as e:
        print(f"SFX error: {e}")
        pass