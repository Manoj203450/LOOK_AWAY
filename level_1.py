import pygame
import sys
import math

from systems.flashlight import draw_flashlight
from systems.moonlight import draw_moonlight, apply_glitch
from systems.hud import draw_hud, set_fps
from systems.boxes import StationaryBox, MovableBox
from systems.fuse_puzzle import FuseBox, run_fuse_puzzle
from systems.pause import run_pause
from systems.potion import PotionInventory
from sprite_loader import AnimatedSprite


def is_point_in_polygon(point, polygon):
    x, y = point.x, point.y
    n = len(polygon)
    inside = False
    px, py = polygon[0]
    for i in range(1, n + 1):
        qx, qy = polygon[i % n]
        if ((py > y) != (qy > y)) and (x < (qx - px) * (y - py) / (qy - py) + px):
            inside = not inside
        px, py = qx, qy
    return inside


def run_death_screen(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font_big   = pygame.font.Font("assets/fonts/menu_font.ttf", 64)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
    except:
        font_big   = pygame.font.SysFont("courier", 64, bold=True)
        font_small = pygame.font.SysFont("courier", 24)

    for alpha in range(0, 180, 3):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((120, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    for alpha in range(0, 256, 3):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    screen.fill((0, 0, 0))
    title    = font_big.render("YOU LOOKED.", True, (180, 30, 30))
    subtitle = font_small.render("the moon has taken you.",
                                 True, (100, 100, 100))
    hint     = font_small.render("press any key to return",
                                 True, (60, 60, 60))
    screen.blit(title,
                (WIDTH//2 - title.get_width()//2,    HEIGHT//2 - 80))
    screen.blit(subtitle,
                (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 + 10))
    screen.blit(hint,
                (WIDTH//2 - hint.get_width()//2,     HEIGHT//2 + 80))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(60)


def run_level1(screen, clock, potion_inv=None, **kwargs):

    if potion_inv is None:
        potion_inv = PotionInventory()

    WIDTH, HEIGHT = screen.get_size()

    MOON_COLOR = (200, 220, 255, 80)
    PLAYER_COL = (180, 210, 255)
    WHITE      = (255, 255, 255)

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except:
        font       = pygame.font.SysFont("courier", 20)
        font_small = pygame.font.SysFont("courier", 14)

    # ROOM BOUNDARIES
    ROOM_LEFT   = 80
    ROOM_TOP    = 100
    ROOM_RIGHT  = 1150
    ROOM_BOTTOM = 620

    # PLAYER
    player_pos   = pygame.Vector2(ROOM_LEFT + 80, ROOM_BOTTOM - 80)
    PLAYER_SIZE  = 48
    PLAYER_SPEED = 4
    health       = 100
    max_health   = 100

    player_sprite = AnimatedSprite(
        "assets/sprites/player.png",
        num_frames=4,
        frame_duration=8,
        scale=1
    )

    # FLASHLIGHT
    FLASHLIGHT_RADIUS = 500
    CONE_ANGLE        = math.radians(45)
    darkness          = pygame.Surface((WIDTH, HEIGHT))
    glitch_intensity  = 0

    # MOONLIGHT BEAM
    moon_beam = [
        (550, ROOM_TOP),
        (650, ROOM_TOP),
        (750, ROOM_BOTTOM),
        (450, ROOM_BOTTOM),
    ]

    # OBJECTS
    stat_obj    = StationaryBox(550, 300, 160, 50)
    mov_obj     = MovableBox(300, 340, 80, 50)
    room_bounds = (ROOM_LEFT, ROOM_TOP, ROOM_RIGHT, ROOM_BOTTOM)

    # FUSE BOXES
    fuse_boxes = [
        FuseBox(ROOM_LEFT - 20, 160),
        FuseBox(400, ROOM_BOTTOM - 20),
    ]

    # EXIT DOOR
    exit_door = pygame.Rect(ROOM_RIGHT - 10, 280, 20, 80)
    door_open = False

    # game_surf is declared here so the pause can access it
    game_surf = pygame.Surface((WIDTH, HEIGHT))

    running = True
    while running:

        # CENTER + ANGLE
        pcx    = player_pos.x + PLAYER_SIZE // 2
        pcy    = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()
        angle  = math.atan2(my - pcy, mx - pcx)

        # CHECK NEARBY FUSE BOX
        active_fuse = None
        near_fuse   = False
        for i, fb in enumerate(fuse_boxes):
            if not fb.fixed and fb.is_near(pcx, pcy):
                active_fuse = i
                near_fuse   = True

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_result = run_pause(screen, clock, game_surf)
                    if pause_result == "continue":
                        pass
                    elif pause_result == "restart":
                        return None
                    elif pause_result == "menu":
                        return "menu"

                if event.key == pygame.K_e and active_fuse is not None:
                    result = run_fuse_puzzle(screen, clock)
                    if result == "solved":
                        fuse_boxes[active_fuse].fixed = True
                if event.key == pygame.K_q:
                    health = potion_inv.use(health, max_health)

        # MOVEMENT
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += PLAYER_SPEED

        moving = (dx != 0 or dy != 0)
        player_sprite.update(moving)

        new_x = player_pos.x + dx
        new_y = player_pos.y + dy

        # Wall collision
        new_x = max(ROOM_LEFT, min(ROOM_RIGHT  - PLAYER_SIZE, new_x))
        new_y = max(ROOM_TOP,  min(ROOM_BOTTOM - PLAYER_SIZE, new_y))

        # Stationary box collision
        new_x, new_y = stat_obj.blocks_player(
                        new_x, new_y, PLAYER_SIZE, player_pos)

        # Movable box collision
        temp_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if temp_rect.colliderect(mov_obj.rect):
            old_box_x = mov_obj.rect.x
            old_box_y = mov_obj.rect.y
            mov_obj.push(dx, dy, temp_rect, room_bounds)
            if mov_obj.rect.colliderect(stat_obj.rect):
                mov_obj.rect.x = old_box_x
                mov_obj.rect.y = old_box_y
                new_x = player_pos.x
                new_y = player_pos.y
            elif (mov_obj.rect.x == old_box_x and
                  mov_obj.rect.y == old_box_y):
                new_x = player_pos.x
                new_y = player_pos.y

        # Hard block player from movable box
        for mb in [mov_obj]:
            player_next = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            if player_next.colliderect(mb.rect):
                player_next_x = pygame.Rect(
                    new_x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)
                player_next_y = pygame.Rect(
                    player_pos.x, new_y, PLAYER_SIZE, PLAYER_SIZE)
                if player_next_x.colliderect(mb.rect):
                    new_x = player_pos.x
                if player_next_y.colliderect(mb.rect):
                    new_y = player_pos.y

        player_pos.x = new_x
        player_pos.y = new_y

        # Recalculate center
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # MOONLIGHT CHECK
        player_in_beam = is_point_in_polygon(
                         pygame.Vector2(pcx, pcy), moon_beam)
        blocked_by_box = (
            stat_obj.blocks_light(player_rect_cur) or
            mov_obj.blocks_light(player_rect_cur)
        )
        in_moonlight = player_in_beam and not blocked_by_box

        if in_moonlight:
            glitch_intensity = min(100, glitch_intensity + 3)
            health -= 0.3
        else:
            glitch_intensity = max(0, glitch_intensity - 1)
        health = max(0, health)

        # DOOR CHECK
        if all(fb.fixed for fb in fuse_boxes):
            door_open = True

        # EXIT CHECK
        if door_open and player_rect_cur.colliderect(exit_door):
            return "level2"

        # DEATH CHECK
        if health <= 0:
            run_death_screen(screen, clock)
            return

        # DRAW onto game_surf (so pause can snapshot it)
        game_surf.fill((15, 15, 25))

        # Room walls
        pygame.draw.rect(game_surf, (50, 55, 70),
                         (ROOM_LEFT, ROOM_TOP,
                          ROOM_RIGHT - ROOM_LEFT,
                          ROOM_BOTTOM - ROOM_TOP), 4)

        # Floor grid
        for gx in range(ROOM_LEFT, ROOM_RIGHT, 60):
            pygame.draw.line(game_surf, (20, 22, 32),
                             (gx, ROOM_TOP), (gx, ROOM_BOTTOM))
        for gy in range(ROOM_TOP, ROOM_BOTTOM, 60):
            pygame.draw.line(game_surf, (20, 22, 32),
                             (ROOM_LEFT, gy), (ROOM_RIGHT, gy))

        # Boxes
        stat_obj.draw(game_surf, font_small)
        mov_obj.draw(game_surf, font_small)

        # Fuse boxes
        for fb in fuse_boxes:
            fb.draw(game_surf, font_small)

        # Exit door
        door_color = (0, 200, 100) if door_open else (60, 80, 60)
        pygame.draw.rect(game_surf, door_color, exit_door)
        if not door_open:
            lock = font_small.render("[LOCKED]", True, (150, 150, 150))
            game_surf.blit(lock,
                           (exit_door.x - 40, exit_door.centery - 8))
        else:
            hint_text = font_small.render("[OPEN]", True, (100, 255, 100))
            game_surf.blit(hint_text,
                           (exit_door.x - 30, exit_door.centery - 8))

        # Moonlight beam
        draw_moonlight(game_surf, moon_beam, MOON_COLOR)

        # Flashlight — dims proportionally to unfixed fuse boxes
        _fixed   = sum(1 for fb in fuse_boxes if fb.fixed)
        _total   = len(fuse_boxes)
        _ambient = int(240 - (_fixed / _total) * 180) if _total > 0 else 240
        draw_flashlight(game_surf, darkness, pcx, pcy, angle,
                        CONE_ANGLE, FLASHLIGHT_RADIUS, ambient_alpha=_ambient)

        # Player sprite
        player_sprite.draw(
            game_surf,
            int(player_pos.x),
            int(player_pos.y)
        )

        # Glitch
        if glitch_intensity > 0:
            apply_glitch(game_surf, glitch_intensity, WIDTH, HEIGHT)

        # Prompt after flashlight for visibility in the dark
        if near_fuse:
            prompt = font.render(
                "PRESS E TO FIX", True, (200, 200, 100))
            game_surf.blit(prompt,
                           (pcx - prompt.get_width()//2, pcy - 50))

        # Blit game_surf to screen
        screen.blit(game_surf, (0, 0))

        # HUD on screen directly
        set_fps(clock.get_fps())
        draw_hud(screen, font, health, max_health,
                 glitch_intensity, False)
        potion_inv.draw(screen, font_small)

        # Fuse box counter - top right
        fixed_count = sum(1 for fb in fuse_boxes if fb.fixed)
        total_count = len(fuse_boxes)
        cnt = font.render(f"POWER:  {fixed_count} / {total_count}",
                          True, (160, 160, 200))
        screen.blit(cnt, (WIDTH - cnt.get_width() - 20, 20))

        pygame.display.flip()
        clock.tick(60)