import pygame
import sys
import math
import random

from systems.flashlight import draw_flashlight
from systems.moonlight import draw_moonlight, apply_glitch
from systems.hud import draw_hud, set_fps
from systems.boxes import StationaryBox, MovableBox
from systems.fuse_puzzle import FuseBox, run_fuse_puzzle
from systems.chest import Chest
from systems.potion import PotionInventory
from systems.dialogue import run_dialogue
from systems.pause import run_pause
from entities.enemy import Enemy
from entities.moon import Moon
from sprite_loader import AnimatedSprite
from systems.audio import play_music, stop_music, play_sfx
from systems.particles import ParticleSystem
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
                (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
    screen.blit(subtitle,
                (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 + 10))
    screen.blit(hint,
                (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 80))
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


def run_level2(screen, clock, potion_inv=None, restart_music=False, start_health=100, **kwargs):
    # Use passed potion inventory or create new one
    if potion_inv is None:
        potion_inv = PotionInventory()
    potion_particles = ParticleSystem()

    if restart_music:
        play_music("assets/audio/audio_1.ogg",
               loop=True, volume=0.3)

    WIDTH, HEIGHT = screen.get_size()

    MOON_COLOR = (200, 220, 255, 80)
    PLAYER_COL = (180, 210, 255)

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

    moon_particles = ParticleSystem()
    moon_part_timer = 0
    MOON_PART_INTERVAL = 6

    # ROOM
    ROOM_LEFT = 60
    ROOM_TOP = 60
    ROOM_RIGHT = 1220
    ROOM_BOTTOM = 660
    room_bounds = (ROOM_LEFT, ROOM_TOP, ROOM_RIGHT, ROOM_BOTTOM)

    # Space hole in the floor (center)
    HOLE_W = 300
    HOLE_H = 200
    HOLE_X = WIDTH  // 2 - HOLE_W // 2
    HOLE_Y = HEIGHT // 2 - HOLE_H // 2
    hole_rect = pygame.Rect(HOLE_X, HOLE_Y, HOLE_W, HOLE_H)

    # PLAYER
    player_pos = pygame.Vector2(ROOM_LEFT + 80, ROOM_BOTTOM - 80)
    PLAYER_SIZE = 48
    PLAYER_SPEED = 4
    health = start_health
    max_health = 100

    player_sprites = AnimatedSprite(
        "assets/sprites/player.png",
        num_frames=4,
        frame_duration=8,
        scale=1
    )

    # FLASHLIGHT
    FLASHLIGHT_RADIUS = 500
    CONE_ANGLE = math.radians(45)
    darkness = pygame.Surface((WIDTH, HEIGHT))
    glitch_intensity = 0

    # MOONLIGHT CIRCLES
    moon_circles = [
        {"center": (300, 200), "radius": 70},
        {"center": (650, 180), "radius": 60},
        {"center": (950, 250), "radius": 75},
        {"center": (200, 450), "radius": 65},
        {"center": (500, 400), "radius": 55},
        {"center": (800, 500), "radius": 70},
        {"center": (1050, 400), "radius": 60},
        {"center": (700, 580), "radius": 65},
    ]

    # STATIONARY BOXES
    stat_boxes = [
        StationaryBox(380, 150, 70, 50),
        StationaryBox(880, 300, 70, 50),
        StationaryBox(850, 180, 70, 50),
        StationaryBox(150, 350, 70, 50),
        StationaryBox(900, 450, 70, 50),
    ]

    # MOVABLE BOXES
    mov_boxes = [
        MovableBox(300, 320, 60, 45),
        MovableBox(600, 480, 60, 45),
        MovableBox(950, 350, 60, 45),
    ]

    # FUSE BOXES
    # placed far from exit to force a run
    fuse_boxes = [
        FuseBox(250, 130),
        FuseBox(750, 130),
        FuseBox(150, 400),   # ← opposite side of exit, final fuse
    ]
    fuse_boxes[2].requires_key = True
    fuse_boxes[2].requires_all = True

    # CHESTS
    chest_wrench = Chest(150,  550, "wrench")
    chest_key = Chest(1050, 150, "key")
    chest_potion = Chest(450,  550, "potion")
    all_chests = [chest_wrench, chest_key, chest_potion]

    # INVENTORY
    has_wrench  = False
    wrench_on_ground = None
    wrenches = []
    WRENCH_SPEED = 10
    wrench_tutorial_shown = False
    has_key = False

    # ENEMY
    enemy = Enemy(400, 200)
    enemy.patrol_points = [
        pygame.Vector2(400, 200),  # top left of hole
        pygame.Vector2(900, 200),  # top right of hole
        pygame.Vector2(900, 550),  # bottom right of hole
        pygame.Vector2(400, 550),  # bottom left of hole
    ]
    enemy_active = False

    valid_room = pygame.Rect(
        ROOM_LEFT, ROOM_TOP,
        ROOM_RIGHT - ROOM_LEFT,
        ROOM_BOTTOM - ROOM_TOP)

    # MOON
    moon = Moon()
    moon_triggered = False

    # EXIT
    exit_door = pygame.Rect(ROOM_RIGHT - 10, HEIGHT//2 - 40, 20, 80)
    door_open = False

    game_surf = pygame.Surface((WIDTH, HEIGHT))

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

    _flood_sfx = None
    try:
        _flood_sfx = pygame.mixer.Sound("assets/audio/sfx/sfx_flood_rise.ogg")
        _flood_sfx.set_volume(0.5 * settings.get("sfx_volume", 1.0))
    except Exception:
        pass

    running = True
    while running:

        # CENTER + ANGLE
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - pcy, mx - pcx)

        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # CHECK NEARBY INTERACTABLES
        active_fuse = None
        near_fuse = False
        near_chest = None

        for i, fb in enumerate(fuse_boxes):
            if not fb.fixed and fb.is_near(pcx, pcy):
                active_fuse = i
                near_fuse = True

        for ch in all_chests:
            if not ch.opened and ch.is_near(pcx, pcy):
                near_chest = ch

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
                        if _flood_sfx: _flood_sfx.stop()
                        if _foot_sfx:  _foot_sfx.stop()
                        return None
                    elif pause_result == "menu":
                        if _flood_sfx: _flood_sfx.stop()
                        if _foot_sfx:  _foot_sfx.stop()
                        return "menu"

                # Fuse box interaction
                if event.key == pygame.K_e and active_fuse is not None:
                    fb = fuse_boxes[active_fuse]
                    needs_key = getattr(fb, "requires_key", False)
                    needs_all = getattr(fb, "requires_all", False)

                    others_done = all(
                        fuse_boxes[i].fixed
                        for i in range(len(fuse_boxes))
                        if i != active_fuse
                    )

                    if needs_all and not others_done:
                        run_dialogue(screen, clock, [
                            ("This one won't budge.",
                             (200, 100, 100)),
                            ("Fix the others first.",
                             (200, 100, 100)),
                        ])
                    elif needs_key and not has_key:
                        run_dialogue(screen, clock, [
                            ("This fuse box is locked.",
                             (200, 100, 100)),
                            ("You need a key to open it.",
                             (200, 100, 100)),
                        ])
                    else:
                        if needs_key and has_key:
                            has_key = False
                        result = run_fuse_puzzle(screen, clock)
                        if result == "solved":
                            fuse_boxes[active_fuse].fix()
                            play_sfx("assets/audio/sfx/sfx_fuse_fix.ogg", volume=0.7)

                # Chest interaction
                elif event.key == pygame.K_e and near_chest is not None:
                    item = near_chest.open()
                    play_sfx("assets/audio/sfx/chest_open.ogg", volume=0.8)
                    if item == "wrench":
                        has_wrench = True
                        if not wrench_tutorial_shown:
                            wrench_tutorial_shown = True
                            run_dialogue(screen, clock, [
                                ("You found a wrench.",
                                 (200, 200, 200)),
                                ("Left click to throw it.",
                                 (200, 200, 100)),
                                ("It will stun enemies on hit.",
                                 (200, 200, 100)),
                                ("Walk over it to pick it back up.",
                                 (200, 200, 100)),
                                ("Don't lose it in the dark...",
                                 (180, 80, 80)),
                            ])
                    elif item == "potion":
                        if potion_inv.add():
                            run_dialogue(screen, clock, [
                                ("Eye drops found.",
                                 (100, 180, 220)),
                                ("Press Q to use.",
                                 (100, 180, 220)),
                                ("Restores 40% health.",
                                 (100, 220, 100)),
                            ])
                    elif item == "key":
                        has_key = True
                        enemy_active = True
                        run_dialogue(screen, clock, [
                            ("You found a key.", (220, 180, 40)),
                            ("...", (200, 200, 200)),
                            ("Something woke up.", (200, 80,  80)),
                            ("RUN.", (255, 50,  50)),
                        ])

                # Potion
                if event.key == pygame.K_q:
                    old_health = health
                    health = potion_inv.use(health, max_health)
                    if health > old_health:
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
                    play_sfx("assets/audio/sfx/sfx_potion.ogg", volume=0.9)


            # Throw wrench
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
                _foot_sfx.set_volume(0.5 * settings.get("sfx_volume", 1.0))
                _foot_sfx.play()
        else:
            if _foot_sfx:
                _foot_sfx.stop()

        new_x = player_pos.x + dx
        new_y = player_pos.y + dy

        # Wall collision
        new_x = max(ROOM_LEFT, min(ROOM_RIGHT  - PLAYER_SIZE, new_x))
        new_y = max(ROOM_TOP,  min(ROOM_BOTTOM - PLAYER_SIZE, new_y))

        # Space hole collision
        temp_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if temp_rect.colliderect(hole_rect):
            new_x = player_pos.x
            new_y = player_pos.y

        # Stationary box collision
        for sb in stat_boxes:
            new_x, new_y = sb.blocks_player(
                            new_x, new_y, PLAYER_SIZE, player_pos)

        # Movable box push
        _box_moved = False
        moving_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        for mb in mov_boxes:
            old_bx = mb.rect.x
            old_by = mb.rect.y
            mb.push(dx, dy, moving_rect, room_bounds)
            if mb.rect.x != old_bx or mb.rect.y != old_by:
                _box_moved = True
            for sb in stat_boxes:
                if mb.rect.colliderect(sb.rect):
                    mb.rect.x = old_bx
                    mb.rect.y = old_by
                    new_x = player_pos.x
                    new_y = player_pos.y
            if mb.rect.colliderect(hole_rect):
                mb.rect.x = old_bx
                mb.rect.y = old_by

        if _box_moved:
            if _box_sfx and _box_sfx.get_num_channels() == 0:
                _box_sfx.set_volume(0.5 * settings.get("sfx_volume", 1.0))
                _box_sfx.play()
        else:
            if _box_sfx:
                _box_sfx.stop()

        # Hard block player from movable boxes
        for mb in mov_boxes:
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

        # Recalculate
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # MOONLIGHT DAMAGE
        taking_damage = False
        for c in moon_circles:
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

        # Moon flood damage
        if moon.is_flooding():
            taking_damage = True
            play_sfx("assets/audio/sfx/sfx_damage.ogg", volume=0.075)
            health -= moon.get_flood_damage()

        if taking_damage:
            glitch_intensity = min(100, glitch_intensity + 3)
            play_sfx("assets/audio/sfx/sfx_damage.ogg", volume=0.075)
            health -= 0.3
        else:
            glitch_intensity = max(0, glitch_intensity - 1)
        health = max(0, health)

        # ENEMY UPDATE
        if enemy_active:
            enemy.update(player_pos, PLAYER_SIZE,
                         valid_rooms=[valid_room],
                         hole_rect=hole_rect)
            if enemy.get_rect().colliderect(player_rect_cur):
                if enemy.state == "chase":
                    play_sfx("assets/audio/sfx/sfx_damage.ogg", volume=0.075)
                    health -= 0.5

        # WRENCH UPDATE
        for w in wrenches[:]:
            w["pos"] += w["vel"]
            w["life"] -= 1
            w["rotation"] += 20

            wrench_rect = pygame.Rect(w["pos"].x, w["pos"].y, 10, 10)
            in_bounds = valid_room.contains(wrench_rect)

            if not in_bounds or w["life"] <= 0:
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrench_on_ground.x = max(ROOM_LEFT + 10,
                    min(ROOM_RIGHT  - 10, wrench_on_ground.x))
                wrench_on_ground.y = max(ROOM_TOP  + 10,
                    min(ROOM_BOTTOM - 10, wrench_on_ground.y))
                wrenches.remove(w)
                continue

            wr = pygame.Rect(w["pos"].x, w["pos"].y, 10, 10)
            if enemy_active and wr.colliderect(enemy.get_rect()):
                enemy.stun(hit_x=w["pos"].x, hit_y=w["pos"].y)
                play_sfx("assets/audio/sfx/sfx_wrench_hit.ogg", volume=0.9)
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrenches.remove(w)

        if wrench_on_ground:
            gr = pygame.Rect(
                wrench_on_ground.x, wrench_on_ground.y, 16, 16)
            if player_rect_cur.colliderect(gr):
                has_wrench = True
                wrench_on_ground = None

        # MOON TRIGGER
        if all(fb.fixed for fb in fuse_boxes) and not moon_triggered:
            moon_triggered = True
            moon.trigger()
            if _flood_sfx:
                _flood_sfx.play(-1)
            play_sfx("assets/audio/sfx/sfx_door_open.ogg", volume=0.6)
            door_open = True

            run_dialogue(screen, clock, [
                ("All power restored.", (200, 200, 200)),
                ("...", (200, 200, 200)),
                ("Something is wrong.", (200, 80,  80)),
                ("DON'T LOOK AT THE MOON.", (255, 50,  50)),
            ])

            stop_music()
            play_music("assets/audio/moon_theme.ogg",
                       loop=True, volume=0.5)

        moon.update()

        if moon_triggered:
            moon_part_timer += 1
            if moon_part_timer >= MOON_PART_INTERVAL:
                moon_part_timer = 0
                moon_particles.emit(
                    HOLE_X + random.randint(0, 10),
                    HOLE_Y + random.randint(0, HOLE_H),
                    colour=(180, 220, 255),
                    count=2, speed=0.8, size=2, lifetime=50)
                moon_particles.emit(
                    HOLE_X + HOLE_W + random.randint(-10, 0),
                    HOLE_Y + random.randint(0, HOLE_H),
                    colour=(180, 220, 255),
                    count=2, speed=0.8, size=2, lifetime=50)
                moon_particles.emit(
                    HOLE_X + random.randint(0, HOLE_W),
                    HOLE_Y + random.randint(0, 10),
                    colour=(200, 230, 255),
                    count=2, speed=0.6, size=2, lifetime=40)
                moon_particles.emit(
                    HOLE_X + random.randint(0, HOLE_W),
                    HOLE_Y + HOLE_H + random.randint(-10, 0),
                    colour=(200, 230, 255),
                    count=2, speed=0.6, size=2, lifetime=40)
        moon_particles.update()

        # EXIT CHECK
        if door_open and player_rect_cur.colliderect(exit_door):
            if not has_wrench:
                pass  # show warning in draw section
            else:
                if _flood_sfx: _flood_sfx.stop()
                if _foot_sfx:  _foot_sfx.stop()
                return "level3", health

        # DEATH CHECK
        if health <= 0:
            stop_music()
            if _flood_sfx: _flood_sfx.stop()
            if _foot_sfx:  _foot_sfx.stop()
            run_death_screen(screen, clock)
            return

        # DRAW
        shake_x, shake_y = moon.get_shake_offset()
        game_surf.fill((5, 5, 15))

        # Room background
        pygame.draw.rect(game_surf, (15, 16, 25),
                         (ROOM_LEFT, ROOM_TOP,
                          ROOM_RIGHT - ROOM_LEFT,
                          ROOM_BOTTOM - ROOM_TOP))
        pygame.draw.rect(game_surf, (50, 55, 70),
                         (ROOM_LEFT, ROOM_TOP,
                          ROOM_RIGHT - ROOM_LEFT,
                          ROOM_BOTTOM - ROOM_TOP), 3)

        # Floor grid
        for gx in range(ROOM_LEFT, ROOM_RIGHT, 60):
            pygame.draw.line(game_surf, (20, 22, 32),
                             (gx, ROOM_TOP), (gx, ROOM_BOTTOM))
        for gy in range(ROOM_TOP, ROOM_BOTTOM, 60):
            pygame.draw.line(game_surf, (20, 22, 32),
                             (ROOM_LEFT, gy), (ROOM_RIGHT, gy))

        # Space hole
        pygame.draw.rect(game_surf, (0, 0, 8), hole_rect)
        random.seed(42)
        for _ in range(40):
            sx = HOLE_X + random.randint(0, HOLE_W)
            sy = HOLE_Y + random.randint(0, HOLE_H)
            pygame.draw.circle(game_surf, (255, 255, 255), (sx, sy), 1)
        random.seed()
        pygame.draw.rect(game_surf, (40, 45, 55), hole_rect, 4)
        pygame.draw.rect(game_surf, (20, 22, 30),
                         (HOLE_X + 4, HOLE_Y + 4,
                          HOLE_W - 8, HOLE_H - 8), 2)
        crack_lines = [
            ((HOLE_X, HOLE_Y),
             (HOLE_X - 30, HOLE_Y - 20)),
            ((HOLE_X + HOLE_W, HOLE_Y),
             (HOLE_X + HOLE_W + 25, HOLE_Y - 15)),
            ((HOLE_X, HOLE_Y + HOLE_H),
             (HOLE_X - 20, HOLE_Y + HOLE_H + 25)),
            ((HOLE_X + HOLE_W, HOLE_Y + HOLE_H),
             (HOLE_X + HOLE_W + 20, HOLE_Y + HOLE_H + 20)),
            ((HOLE_X + 100, HOLE_Y),
             (HOLE_X + 80, HOLE_Y - 35)),
            ((HOLE_X + 200, HOLE_Y + HOLE_H),
             (HOLE_X + 220, HOLE_Y + HOLE_H + 30)),
        ]
        for start, end in crack_lines:
            pygame.draw.line(game_surf, (60, 65, 75), start, end, 2)

        # Moon rises through hole
        if moon_triggered:
            moon.draw_moon(game_surf, hole_rect)

        if moon_triggered:
            moon.draw_moon(game_surf, hole_rect)
        moon_particles.draw(game_surf)

        # Moonlight circles
        for c in moon_circles:
            cx, cy = c["center"]
            r = c["radius"]
            circ = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(circ, (200, 220, 255, 70), (r, r), r)
            game_surf.blit(circ, (cx - r, cy - r))

        # Stationary boxes
        for sb in stat_boxes:
            sb.draw(game_surf, font_small)

        # Movable boxes
        for mb in mov_boxes:
            mb.draw(game_surf, font_small)

        # Chests
        for ch in all_chests:
            ch.draw(game_surf, font_small)

        # Fuse boxes
        for fb in fuse_boxes:
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
                           (exit_door.x - 50, exit_door.centery - 8))

        # Enemy
        if enemy_active:
            enemy.draw(game_surf)
        else:
            pygame.draw.rect(game_surf, (80, 80, 80),
                             (enemy.pos.x, enemy.pos.y,
                              enemy.size, enemy.size))
            dorm = font_small.render("z", True, (120, 120, 120))
            game_surf.blit(dorm,
                           (enemy.pos.x + 8, enemy.pos.y - 14))

        # Wrench on ground
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

        # Moon flood overlay
        moon.draw_flood(game_surf)

        # Flashlight — dims proportionally to unfixed fuse boxes
        _fixed   = sum(1 for fb in fuse_boxes if fb.fixed)
        _total   = len(fuse_boxes)
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
            fb = fuse_boxes[active_fuse]
            needs_key = getattr(fb, "requires_key", False)
            needs_all = getattr(fb, "requires_all", False)
            others_done = all(
                fuse_boxes[i].fixed
                for i in range(len(fuse_boxes))
                if i != active_fuse
            )
            if needs_all and not others_done:
                prompt = font.render(
                    "PRESS E TO FIX  [ FIX OTHERS FIRST ]",
                    True, (200, 100, 100))
                _foot_sfx.stop()
            elif needs_key and not has_key:
                prompt = font.render(
                    "PRESS E TO FIX  [ NEEDS KEY ]",
                    True, (200, 100, 100))
                _foot_sfx.stop()

            else:
                prompt = font.render(
                    "PRESS E TO FIX",
                    True, (200, 200, 100))
                _foot_sfx.stop()
            game_surf.blit(prompt,
                           (pcx - prompt.get_width()//2, pcy - 50))

        if near_chest:
            prompt = font.render(
                "PRESS E TO OPEN", True, (200, 180, 80))
            _foot_sfx.stop()
            game_surf.blit(prompt,
                           (pcx - prompt.get_width()//2, pcy - 50))

        # No wrench warning at exit
        if door_open and player_rect_cur.colliderect(exit_door) \
                     and not has_wrench:
            warn = font.render(
                "[ FIND YOUR WRENCH BEFORE LEAVING ]",
                True, (200, 80, 80))
            game_surf.blit(warn,
                (pcx - warn.get_width()//2, pcy - 70))

        # Moon flood urgency warning
        if moon_triggered and moon.is_flooding():
            flood_ratio = moon.flood_alpha / 255
            if flood_ratio > 0.1:
                urgency = font.render(
                    "! GET TO THE EXIT !",
                    True, (int(255 * flood_ratio), 50, 50))
                game_surf.blit(urgency, (
                    WIDTH//2 - urgency.get_width()//2, 30))

        # Shake
        screen.fill((0, 0, 0))
        screen.blit(game_surf, (shake_x, shake_y))

        # HUD on screen directly (no shake)
        set_fps(clock.get_fps())
        draw_hud(screen, font, health, max_health,
                 glitch_intensity, has_wrench)
        potion_inv.draw(screen, font_small)

        # Fuse box counter
        fixed = sum(1 for fb in fuse_boxes if fb.fixed)
        total = len(fuse_boxes)
        cnt = font.render(f"POWER:  {fixed} / {total}",
                          True, (160, 160, 200))
        screen.blit(cnt, (WIDTH - cnt.get_width() - 20, 20))

        # Key HUD bottom right
        if has_key:
            key_label = font_small.render(
                "[ KEY : READY ]", True, (220, 180, 40))
            screen.blit(key_label, (WIDTH - 160, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)