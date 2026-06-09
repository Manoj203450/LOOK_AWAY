import pygame
import sys
import cv2
import numpy


def run_menu(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    cap = cv2.VideoCapture("assets/menu_video.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_delay = int(1000 / fps)
    last_frame_time = 0
    video_surface = None

    try:
        pygame.mixer.music.load("assets/menu_audio.mp3")
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    try:
        font_title = pygame.font.Font("assets/fonts/mybleedingscars_ot.otf", 90)
    except Exception as e:
        print(f"Title font error: {e}")
        font_title = pygame.font.SysFont("courier", 90, bold=True)

    try:
        font_menu = pygame.font.Font("assets/fonts/menu_font.ttf", 32)
        font_tagline = pygame.font.Font("assets/fonts/menu_font.ttf", 18)
    except Exception:
        font_menu = pygame.font.SysFont("courier", 32)
        font_tagline = pygame.font.SysFont("courier", 18)

    options  = ["START NEW GAME", "SELECT LEVEL", "SETTINGS", "CREDITS", "EXIT"]
    selected = 0

    WHITE = (220, 220, 220)
    RED = (200, 40,  40)
    DIM = (130, 130, 130)
    TAGLINE = (120, 40,  40)

    while True:
        now = pygame.time.get_ticks()

        mx, my = pygame.mouse.get_pos()
        for i in range(len(options)):
            if pygame.Rect(80, 370 + i * 55, 340, 45).collidepoint(mx, my):
                selected = i

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    cap.release()
                    return options[selected]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(len(options)):
                    if pygame.Rect(80, 370 + i * 55, 340, 45).collidepoint(mx, my):
                        cap.release()
                        return options[i]

        if now - last_frame_time >= frame_delay:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                video_surface = pygame.surfarray.make_surface(
                        numpy.rot90(numpy.fliplr(frame)))
            last_frame_time = now

        if video_surface:
            screen.blit(video_surface, (0, 0))
        else:
            screen.fill((0, 0, 0))

        panel_w = 420
        panel = pygame.Surface((panel_w, HEIGHT), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (0, 0))

        # TITLE
        title1 = font_title.render("LOOK", True, (220, 20, 20))
        title2 = font_title.render("AWAY", True, (220, 20, 20))
        screen.blit(title1, (80, 120))
        screen.blit(title2, (80, 210))

        # MENU OPTIONS
        menu_start_y = 370
        for i, option in enumerate(options):
            if i == selected:
                arrow = font_menu.render(">", True, RED)
                screen.blit(arrow, (80, menu_start_y + i * 55))
                text = font_menu.render(option, True, RED)
                screen.blit(text, (115, menu_start_y + i * 55))
            else:
                text = font_menu.render(option, True, DIM)
                screen.blit(text, (115, menu_start_y + i * 55))

        # TAGLINE
        tagline = font_tagline.render(
            "DON'T LOOK TOO LONG.", True, TAGLINE)
        screen.blit(tagline, (80, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)