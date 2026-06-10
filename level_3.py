import pygame
import sys
import math
import random

from systems.flashlight import draw_flashlight
from systems.moonlight import apply_glitch, draw_moonlight
from systems.hud import draw_hud, set_fps
from systems.boxes import StationaryBox, MovableBox
from systems.fuse_puzzle import FuseBox, run_fuse_puzzle
from systems.potion import PotionInventory
from systems.dialogue import run_dialogue
from systems.pause import run_pause
from entities.weeping_angel import WeepingAngel
from sprite_loader import AnimatedSprite
from systems.particles import ParticleSystem
from systems.audio import play_music, stop_music, play_sfx
from systems.settings_manager import settings


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


def in_circle(pcx, pcy, cx, cy, r):
    return math.hypot(pcx - cx, pcy - cy) < r


def run_death_screen(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    try:
        font_big = pygame.font.Font("assets/fonts/menu_font.ttf", 64)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
    except:
        font_big = pygame.font.SysFont("courier", 64, bold=True)
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
    title = font_big.render("YOU LOOKED.", True, (180, 30, 30))
    subtitle = font_small.render("the moon has taken you.",
                                 True, (100, 100, 100))
    hint = font_small.render("press any key to return",
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


def run_level3(screen, clock, start_with_wrench=False,
               potion_inv=None, start_health=100, **kwargs):

    # Use passed potion inventory or create new one
    if potion_inv is None:
        potion_inv = PotionInventory()
    potion_particles = ParticleSystem()

    WIDTH, HEIGHT = screen.get_size()

    WHITE      = (220, 220, 220)
    RED        = (200, 40,  40)

    player_sprites = AnimatedSprite(
        "assets/sprites/player.png",
        num_frames=4,
        frame_duration=8,
        scale=1
    )

    wrench_img = pygame.image.load(
        "assets/sprites/wrench.png"
    ).convert_alpha()

    wrench_img = pygame.transform.scale(
        wrench_img, (24, 24)
    )

    try:
        font = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except:
        font = pygame.font.SysFont("courier", 20)
        font_small = pygame.font.SysFont("courier", 14)

    # ROOMS
    ROOM_A  = pygame.Rect(40,  40,  380, 280)   # top left  (spawn)
    ROOM_B  = pygame.Rect(500, 40,  420, 280)   # top right
    ROOM_C  = pygame.Rect(40,  400, 380, 280)   # bottom left
    ROOM_D  = pygame.Rect(500, 400, 420, 280)   # bottom right (exit)

    CORR_AB = pygame.Rect(415, 100, 90,  130)    # A → B
    CORR_AC = pygame.Rect(100, 315, 130, 90)    # A → C
    CORR_BD = pygame.Rect(575, 315, 130, 90)    # B → D
    CORR_CD = pygame.Rect(415, 475, 90,  130)    # C → D

    all_rooms = [ROOM_A, ROOM_B, ROOM_C, ROOM_D,
                 CORR_AB, CORR_AC, CORR_BD, CORR_CD]

    # PLAYER
    player_pos = pygame.Vector2(ROOM_A.x + 60, ROOM_A.centery)
    PLAYER_SIZE = 48
    PLAYER_SPEED = 4
    health = start_health
    max_health = 100

    # FLASHLIGHT
    FLASHLIGHT_RADIUS = 500
    CONE_ANGLE = math.radians(45)
    darkness = pygame.Surface((WIDTH, HEIGHT))
    glitch_intensity  = 0

    # WRENCH
    has_wrench = start_with_wrench
    wrench_on_ground = None
    wrenches = []
    WRENCH_SPEED = 10

    # MOONLIGHT
    moon_circles_a = [
        {"center": (ROOM_A.x + 200, ROOM_A.y + 140), "radius": 55},
    ]
    moon_beams_b = [
        [(ROOM_B.x + 100, ROOM_B.y),
         (ROOM_B.x + 180, ROOM_B.y),
         (ROOM_B.x + 280, ROOM_B.bottom),
         (ROOM_B.x + 160, ROOM_B.bottom)],
        [(ROOM_B.x + 240, ROOM_B.y),
         (ROOM_B.x + 340, ROOM_B.y),
         (ROOM_B.x + 400, ROOM_B.bottom),
         (ROOM_B.x + 300, ROOM_B.bottom)],
    ]
    moon_circles_c = [
        {"center": (ROOM_C.x + 120, ROOM_C.y + 100), "radius": 50},
        {"center": (ROOM_C.x + 280, ROOM_C.y + 200), "radius": 50},
    ]
    moon_circles_d = [
        {"center": (ROOM_D.x + 300, ROOM_D.y + 140), "radius": 55},
    ]

    # BOXES
    stat_boxes = [
        StationaryBox(ROOM_B.x + 80,  ROOM_B.y + 120, 60, 40),
        StationaryBox(ROOM_B.x + 240, ROOM_B.y + 80,  60, 40),
        StationaryBox(ROOM_C.x + 100, ROOM_C.y + 60,  60, 40),
        StationaryBox(ROOM_C.x + 220, ROOM_C.y + 160, 60, 40),
        StationaryBox(ROOM_D.x + 80,  ROOM_D.y + 80,  60, 40),
        StationaryBox(ROOM_D.x + 200, ROOM_D.y + 180, 60, 40),
    ]

    mov_boxes = [
        MovableBox(ROOM_A.x + 160, ROOM_A.y + 180, 55, 40),
        MovableBox(ROOM_C.x + 180, ROOM_C.y + 100, 55, 40),
    ]

    room_bounds_a = (ROOM_A.x, ROOM_A.y, ROOM_A.right, ROOM_A.bottom)
    room_bounds_c = (ROOM_C.x, ROOM_C.y, ROOM_C.right, ROOM_C.bottom)

    # FUSE BOXES
    fuse_a = FuseBox(ROOM_A.x + 30, ROOM_A.y + 30)
    fuse_b = FuseBox(ROOM_B.right - 60, ROOM_B.y + 30)
    fuse_d = FuseBox(ROOM_D.x + 30, ROOM_D.bottom - 60)
    all_fuses = [fuse_a, fuse_b, fuse_d]

    # WEEPING ANGELS
    angel_b = WeepingAngel(ROOM_B.x + 200, ROOM_B.y + 150)
    angel_d = WeepingAngel(ROOM_D.x + 200, ROOM_D.y + 100)
    angel_b.speed = 2.0
    angel_d.speed = 2.0

    # EXIT
    exit_door = pygame.Rect(ROOM_D.right - 10,
                            ROOM_D.centery - 30, 20, 60)
    door_open = False

    # DIALOGUE FLAGS
    intro_done = False
    angel_warned = False
    question_asked = False
    fuse_b_dialogue = False
    exit_dialogue_done = False

    # DRAW
    game_surf = pygame.Surface((WIDTH, HEIGHT))
    game_surf.fill((5, 5, 15))

    _foot_sfx = None
    try:
        _foot_sfx = pygame.mixer.Sound("assets/audio/sfx/sfx_footstep.ogg")
    except Exception:
        pass

    _box_sfx = None
    try:
        _box_sfx = pygame.mixer.Sound("assets/audio/sfx/sfx_box_push.ogg")
    except Exception:
        pass

    _angel_sfx = None
    try:
        _angel_sfx = pygame.mixer.Sound("assets/audio/sfx/sfx_angel_move.ogg")
    except Exception:
        pass

    _prev_angel_b_frozen = True
    _prev_angel_d_frozen = True
    running = True
    while running:

        # CENTER + ANGLE
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - pcy, mx - pcx)

        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # Which room is player in
        in_room_a = ROOM_A.collidepoint(pcx, pcy)
        in_room_b = ROOM_B.collidepoint(pcx, pcy)
        in_room_c = ROOM_C.collidepoint(pcx, pcy)
        in_room_d = ROOM_D.collidepoint(pcx, pcy)

        # DIALOGUE TRIGGERS
        if not intro_done:
            intro_done = True
            run_dialogue(screen, clock, [
                ("I made it this far...", WHITE),
                ("...", WHITE),
                ("Who are you?", WHITE),
                ("...", RED),
                ("Why do you keep warning me?", WHITE),
                ("...", RED),
                ("...Hello?", WHITE),
                ("DON'T MOVE.", RED),
            ], black_bg=True)

        if in_room_b and not angel_warned:
            angel_warned = True
            run_dialogue(screen, clock, [
                ("Something is in here.", WHITE),
                ("DON'T LOOK AWAY.", RED),
                ("Keep your light on it.", RED),
            ])

        if in_room_c and not question_asked:
            question_asked = True
            run_dialogue(screen, clock, [
                ("Are you even real?", WHITE),
                ("...", RED),
                ("Or am I just losing my mind?", WHITE),
                ("WATCH YOUR STEP.", RED),
            ])

        if in_room_b and fuse_b.fixed and not fuse_b_dialogue:
            fuse_b_dialogue = True
            run_dialogue(screen, clock, [
                ("One more...", WHITE),
                ("...", RED),
                ("Where are you taking me?", WHITE),
                ("KEEP MOVING.", RED),
            ])

        # CHECK NEARBY FUSE BOXES
        active_fuse = None
        near_fuse = False

        for i, fb in enumerate(all_fuses):
            if not fb.fixed and fb.is_near(pcx, pcy):
                active_fuse = i
                near_fuse = True

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
                        if _angel_sfx: _angel_sfx.stop()
                        if _foot_sfx: _foot_sfx.stop()
                        return None
                    elif pause_result == "menu":
                        if _angel_sfx: _angel_sfx.stop()
                        if _foot_sfx: _foot_sfx.stop()
                        return "menu"

                if event.key == pygame.K_e and active_fuse is not None:
                    result = run_fuse_puzzle(screen, clock)
                    if result == "solved":
                        all_fuses[active_fuse].fix()
                        play_sfx("assets/audio/sfx/sfx_fuse_fix.ogg", volume=0.7)
                        if all(fb.fixed for fb in all_fuses):
                            door_open = True
                            play_sfx("assets/audio/sfx/sfx_door_open.ogg", volume=0.6)
                if event.key == pygame.K_q:
                    old_health = health
                    health = potion_inv.use(health, max_health)
                    if health > old_health:
                        play_sfx("assets/audio/sfx/sfx_potion.ogg", volume=0.9)
                        potion_particles.emit(
                            pcx, pcy,
                            colour=(100, 220, 100),
                            count=15,
                            speed=2.5,
                            size=3,
                            lifetime=40
                        )
                        potion_particles.emit(
                            pcx, pcy,
                            colour=(255, 255, 255),
                            count=8,
                            speed=4.0,
                            size=2,
                            lifetime=25
                        )


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and has_wrench:
                    dx_w = mx - pcx
                    dy_w = my - pcy
                    dist = math.hypot(dx_w, dy_w)
                    if dist > 0:
                        has_wrench = False
                        play_sfx("assets/audio/sfx/sfx_wrench_throw.ogg", volume=0.8)
                        wrenches.append({
                            "pos": pygame.Vector2(pcx, pcy),
                            "vel": pygame.Vector2(
                                        dx_w/dist * WRENCH_SPEED,
                                        dy_w/dist * WRENCH_SPEED),
                            "life": 30,
                            "rotation": 0
                        })

        # MOVEMENT
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += PLAYER_SPEED

        moving = (dx != 0 or dy != 0)
        player_sprites.update(moving)
        if moving:
            if _foot_sfx and _foot_sfx.get_num_channels() == 0:
                _foot_sfx.set_volume(0.9 * settings.get("sfx_volume", 1.0))
                _foot_sfx.play()
        else:
            if _foot_sfx:
                _foot_sfx.stop()

        new_x = player_pos.x + dx
        new_y = player_pos.y + dy

        # Wall collision
        def in_valid_area(x, y):
            test_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
            # Player is valid if ALL four corners are inside any room
            corners = [
                (test_rect.left, test_rect.top),
                (test_rect.right, test_rect.top),
                (test_rect.left, test_rect.bottom),
                (test_rect.right, test_rect.bottom),
            ]
            return all(
                any(room.collidepoint(cx, cy) for room in all_rooms)
                for cx, cy in corners
            )

        if not in_valid_area(new_x, player_pos.y):
            new_x = player_pos.x
        if not in_valid_area(player_pos.x, new_y):
            new_y = player_pos.y

        # Hard clamp to screen
        new_x = max(0, min(WIDTH - PLAYER_SIZE, new_x))
        new_y = max(0, min(HEIGHT - PLAYER_SIZE, new_y))

        # Stationary box collision
        for sb in stat_boxes:
            new_x, new_y = sb.blocks_player(
                            new_x, new_y, PLAYER_SIZE, player_pos)

        # Movable box push
            # Movable box push
            _box_moved = False  # reset every frame
            moving_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            for mb in mov_boxes:
                old_bx = mb.rect.x
                old_by = mb.rect.y
                mb.push(dx, dy, moving_rect,
                        room_bounds_a,
                        valid_rooms=all_rooms)
                if mb.rect.x != old_bx or mb.rect.y != old_by:
                    _box_moved = True  # box actually moved
                for sb in stat_boxes:
                    if mb.rect.colliderect(sb.rect):
                        mb.rect.x = old_bx
                        mb.rect.y = old_by
                        new_x = player_pos.x
                        new_y = player_pos.y

                if mb.rect.x == old_bx and mb.rect.y == old_by:
                    player_next = pygame.Rect(
                        new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
                    if player_next.colliderect(mb.rect):
                        new_x = player_pos.x
                        new_y = player_pos.y

            if _box_moved:  # play/stop after loop
                if _box_sfx and _box_sfx.get_num_channels() == 0:
                    _box_sfx.set_volume(0.9 * settings.get("sfx_volume", 1.0))
                    _box_sfx.play()
            else:
                if _box_sfx:
                    _box_sfx.stop()

        # Hard block
        for mb in mov_boxes:
            player_next = pygame.Rect(
                new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
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

        # Recalculate
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # UPDATE WEEPING ANGELS
        all_fixed = all(fb.fixed for fb in all_fuses)
        if not all_fixed:
            angel_b.update(player_pos, PLAYER_SIZE,
                           angle, CONE_ANGLE, FLASHLIGHT_RADIUS,
                           valid_rooms=all_rooms)
            angel_d.update(player_pos, PLAYER_SIZE,
                           angle, CONE_ANGLE, FLASHLIGHT_RADIUS,
                           valid_rooms=all_rooms)

        any_angel_moving = not angel_b.frozen or not angel_d.frozen
        if any_angel_moving:
            if _angel_sfx and _angel_sfx.get_num_channels() == 0:
                _angel_sfx.set_volume(0.75 * settings.get("sfx_volume", 1.0))
                _angel_sfx.play(-1)
        else:
            if _angel_sfx:
                _angel_sfx.stop()

        for angel in [angel_b, angel_d]:
            if angel.get_rect().colliderect(player_rect_cur):
                health = 0

        # WRENCH UPDATE
        for w in wrenches[:]:
            w["pos"] += w["vel"]
            w["life"] -= 1
            w["rotation"] += 20

            wrench_rect = pygame.Rect(w["pos"].x, w["pos"].y, 10, 10)
            in_bounds = any(room.contains(wrench_rect)
                              for room in all_rooms)

            if not in_bounds or w["life"] <= 0:
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrench_on_ground.x = max(40, min(WIDTH  - 10,
                                         wrench_on_ground.x))
                wrench_on_ground.y = max(40, min(HEIGHT - 10,
                                         wrench_on_ground.y))
                wrenches.remove(w)
                continue

        if wrench_on_ground:
            gr = pygame.Rect(
                wrench_on_ground.x, wrench_on_ground.y, 16, 16)
            if player_rect_cur.colliderect(gr):
                has_wrench = True
                wrench_on_ground = None

        # MOONLIGHT DAMAGE
        taking_damage = False

        all_circles = moon_circles_a + moon_circles_c + moon_circles_d
        for c in all_circles:
            if in_circle(pcx, pcy, *c["center"], c["radius"]):
                blocked = False
                for mb in mov_boxes:
                    if mb.blocks_light(player_rect_cur):
                        blocked = True
                for sb in stat_boxes:
                    if sb.blocks_light(player_rect_cur):
                        blocked = True
                if not blocked:
                    taking_damage = True

        # Beam check with box blocking
        for beam in moon_beams_b:
            if is_point_in_polygon(pygame.Vector2(pcx, pcy), beam):
                blocked = False
                # Check boxes against beam
                for mb in mov_boxes:
                    if mb.blocks_beam(player_rect_cur, beam):
                        blocked = True
                for sb in stat_boxes:
                    if sb.blocks_beam(player_rect_cur, beam):
                        blocked = True
                if not blocked:
                    taking_damage = True

        if taking_damage:
            glitch_intensity = min(100, glitch_intensity + 3)
            play_sfx("assets/audio/sfx/sfx_damage.ogg", volume=0.15)
            health -= 0.3
        else:
            glitch_intensity = max(0, glitch_intensity - 4)
        health = max(0, health)

        # DOOR CHECK
        if all(fb.fixed for fb in all_fuses):
            door_open = True

        # EXIT CHECK
        if door_open and player_rect_cur.colliderect(exit_door):
            if not has_wrench:
                pass  # warning shown in draw section
            elif not exit_dialogue_done:
                exit_dialogue_done = True

                # Fade to black
                for alpha in range(0, 256, 5):
                    screen.fill((0, 0, 0))
                    fade = pygame.Surface(screen.get_size())
                    fade.fill((0, 0, 0))
                    fade.set_alpha(alpha)
                    screen.blit(fade, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)

                # Dialogue on black screen
                screen.fill((0, 0, 0))
                run_dialogue(screen, clock, [
                    ("You are close.", RED),
                    ("Who are you?",  WHITE),
                    ("Go to the canons.", RED),
                    ("Restore all powers to activate it.", RED),
                    ("What?", WHITE),
                    ("The moon can be destroyed.", RED),
                    ("The canons... I remember...", WHITE),
                    ("...", RED),
                    ("The canons are your only hope.", RED),
                    ("Lets destroy this big rock in space.", WHITE),
                ], black_bg=True)
                if _angel_sfx: _angel_sfx.stop()
                if _foot_sfx: _foot_sfx.stop()
                return "level4", health
            else:
                if _angel_sfx: _angel_sfx.stop()
                if _foot_sfx: _foot_sfx.stop()
                return "level4", health

        # DEATH CHECK
        if health <= 0:
            if _angel_sfx: _angel_sfx.stop()
            if _foot_sfx: _foot_sfx.stop()
            run_death_screen(screen, clock)
            return

        # Draw rooms
        def draw_room(surf, rect, wall_color=(50, 55, 70)):
            pygame.draw.rect(surf, (15, 16, 25), rect)
            pygame.draw.rect(surf, wall_color, rect, 3)
            for gx in range(rect.x, rect.right, 50):
                pygame.draw.line(surf, (20, 22, 32),
                                 (gx, rect.y), (gx, rect.bottom))
            for gy in range(rect.y, rect.bottom, 50):
                pygame.draw.line(surf, (20, 22, 32),
                                 (rect.x, gy), (rect.right, gy))

        for room in all_rooms:
            draw_room(game_surf, room)

        # Room labels
        for label, rect in [("A", ROOM_A), ("B", ROOM_B),
                             ("C", ROOM_C), ("D", ROOM_D)]:
            l = font_small.render(label, True, (35, 40, 50))
            game_surf.blit(l, (rect.x + 8, rect.y + 6))

        # Moonlight circles
        def draw_circle_light(surf, cx, cy, r):
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 220, 255, 70), (r, r), r)
            surf.blit(s, (cx - r, cy - r))

        for c in all_circles:
            draw_circle_light(game_surf, *c["center"], c["radius"])

        # Room B beams
        for beam in moon_beams_b:
            draw_moonlight(game_surf, beam)

        # Stationary boxes
        for sb in stat_boxes:
            sb.draw(game_surf, font_small)

        # Movable boxes
        for mb in mov_boxes:
            mb.draw(game_surf, font_small)

        # Fuse boxes
        for fb in all_fuses:
            fb.draw(game_surf, font_small)

        # Exit door
        door_color = (0, 200, 100) if door_open else (60, 80, 60)
        pygame.draw.rect(game_surf, door_color, exit_door)
        if not door_open:
            lock = font_small.render("[LOCKED]", True, (150, 150, 150))
            game_surf.blit(lock,
                           (exit_door.x - 60, exit_door.centery - 8))
        else:
            ex = font_small.render("[EXIT]", True, (100, 255, 100))
            game_surf.blit(ex,
                           (exit_door.x + 5, exit_door.centery - 8))

        # Weeping angels
        angel_b.draw(game_surf)
        angel_d.draw(game_surf)

        # Wrench on ground
        if wrench_on_ground:
            if wrench_on_ground:
                game_surf.blit(
                    wrench_img,
                    (
                        int(wrench_on_ground.x - 12),
                        int(wrench_on_ground.y - 12)
                    )
                )

        # Flying wrenches
        for w in wrenches:
            rotated = pygame.transform.rotate(
                wrench_img,
                w["rotation"]
            )

            rect = rotated.get_rect(center=(
                int(w["pos"].x),
                int(w["pos"].y)
            ))

            game_surf.blit(rotated, rect)

        # Flashlight — dims proportionally to unfixed fuses
        _fixed   = sum(1 for f in all_fuses if f.fixed)
        _total   = len(all_fuses)
        _ambient = int(240 - (_fixed / _total) * 180) if _total > 0 else 240
        draw_flashlight(game_surf, darkness, pcx, pcy, angle,
                        CONE_ANGLE, FLASHLIGHT_RADIUS, ambient_alpha=_ambient)

        # Player sprite
        player_sprites.draw(
            game_surf,
            int(player_pos.x),
            int(player_pos.y)
        )

        potion_particles.update()
        potion_particles.draw(game_surf)

        # Glitch
        if glitch_intensity > 0:
            apply_glitch(game_surf, glitch_intensity, WIDTH, HEIGHT)

        # Prompts
        if near_fuse:
            prompt = font.render(
                "PRESS E TO FIX", True, (200, 200, 100))
            _foot_sfx.stop()
            game_surf.blit(prompt, (pcx - prompt.get_width()//2, pcy - 50))

        # No wrench warning at exit
        if door_open and player_rect_cur.colliderect(exit_door) \
                     and not has_wrench:
            warn = font.render(
                "[ FIND YOUR WRENCH BEFORE LEAVING ]",
                True, (200, 80, 80))
            game_surf.blit(warn,
                (pcx - warn.get_width()//2, pcy - 70))

        screen.fill((0, 0, 0))
        screen.blit(game_surf, (0, 0))

        # HUD
        set_fps(clock.get_fps())
        draw_hud(screen, font, health, max_health,
                 glitch_intensity, has_wrench)
        potion_inv.draw(screen, font_small)

        # Fuse box counter - top right
        fixed_count = sum(1 for fb in all_fuses if fb.fixed)
        total_count = len(all_fuses)
        cnt = font.render(f"POWER:  {fixed_count} / {total_count}",
                          True, (160, 160, 200))
        screen.blit(cnt, (WIDTH - cnt.get_width() - 20, 20))

        pygame.display.flip()
        clock.tick(60)