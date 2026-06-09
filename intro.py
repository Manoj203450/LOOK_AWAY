import pygame
import sys

def run_intro(screen, clock):
        BLACK = (0, 0, 0)
        WHITE = (220, 220, 220)
        DIM = (100, 100, 100)
        RED = (180, 30, 30)

        try:
            font_dialogue = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
            font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
        except:
            font_dialogue = pygame.font.SysFont("courier", 24)
            font_small = pygame.font.SysFont("courier", 16)


        dialogue = [
            ("... ... ...", DIM, 800),
            ("SYSTEM REBOOT INITIATED.", DIM, 600),
            ("HULL BREACH DETECTED.", RED, 600),
            ("LIFE SUPPORT: CRITICAL", RED, 800),
            ("", WHITE, 400),
            ("...", WHITE, 600),
            ("My head...", WHITE, 700),
            ("What happened to the ship?", WHITE, 800),
            ("", WHITE, 300),
            ("I need to find a way out.", WHITE, 900),
            ("But something feels... wrong.", WHITE, 900),
            ("", WHITE, 300),
            ("The moon.", RED, 600),
            ("Don't look at the moon.", RED, 1200),
        ]

        def typewriter(screen, font, text, color, x, y, speed=30):
            displayed = ""
            for char in text:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if _click_sfx: _click_sfx.stop()
                            return False  # skip entire intro
                        if event.key == pygame.K_SPACE:
                            if _click_sfx: _click_sfx.stop()
                            # skip to full line instantly
                            displayed = text
                            screen.fill(BLACK)
                            render = font.render(displayed, True, color)
                            screen.blit(render, (x, y))
                            hint = font_small.render(
                                "SPACE - skip line  |  ESC - skip intro",
                                True, (60, 60, 60))
                            screen.blit(hint, (40, screen.get_height() - 40))
                            pygame.display.flip()
                            return True

                displayed += char
                if _click_sfx and _click_sfx.get_num_channels() == 0:
                    _click_sfx.play()
                screen.fill(BLACK)
                render = font.render(displayed, True, color)
                screen.blit(render, (x, y))
                hint = font_small.render(
                    "SPACE - skip line  |  ESC - skip intro",
                    True, (60, 60, 60))
                screen.blit(hint, (40, screen.get_height() - 40))
                pygame.display.flip()
                clock.tick(speed)  # lower = faster typing

            if _click_sfx: _click_sfx.stop()
            return True

        fade_surf = pygame.Surface(screen.get_size())
        fade_surf.fill(BLACK)
        for alpha in range (255, 0, -5):
            fade_surf.set_alpha(alpha)
            screen.fill(BLACK)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            clock.tick(60)

        _click_sfx = None
        try:
            from systems.settings_manager import settings as _s
            _click_sfx = pygame.mixer.Sound("assets/audio/sfx/sfx_dialogue_click.ogg")
            _click_sfx.set_volume(0.3 * _s.get("sfx_volume", 1.0))
        except Exception:
            pass

        for (text, color, pause) in dialogue:
            if text == "":
                pygame.time.wait(pause)
                continue

            result = typewriter(screen, font_dialogue, text, color, 80,
                                screen.get_height() // 2, speed=28)

            if not result:
                break

            pygame.time.wait(pause)

        fade_surf.set_alpha(0)
        for alpha in range(0, 256, 5):
            fade_surf.set_alpha(alpha)
            screen.fill(BLACK)
            screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            clock.tick(60)