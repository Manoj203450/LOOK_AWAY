import pygame
import sys
import math

from systems.flashlight import draw_flashlight
from systems.moonlight import apply_glitch
from systems.hud import draw_hud
from systems.boxes import StationaryBox, MovableBox
from systems.fuse_puzzle import FuseBox, run_fuse_puzzle
from systems.potion import PotionInventory
from systems.dialogue import run_dialogue
from systems.pause import run_pause
from systems.audio import play_music, stop_music
from entities.shade import Shade
from sprite_loader import AnimatedSprite


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def run_death_screen(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    try:
        font_big   = pygame.font.Font("assets/fonts/menu_font.ttf", 64)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
    except Exception:
        font_big   = pygame.font.SysFont("courier", 64, bold=True)
        font_small = pygame.font.SysFont("courier", 24)

    for alpha in range(0, 256, 4):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    screen.fill((0, 0, 0))
    title    = font_big.render("YOU LOOKED.", True, (180, 30, 30))
    subtitle = font_small.render("the light woke them.", True, (100, 100, 100))
    hint     = font_small.render("press any key to return", True, (60, 60, 60))
    screen.blit(title,    (WIDTH//2 - title.get_width()//2,    HEIGHT//2 - 80))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 + 10))
    screen.blit(hint,     (WIDTH//2 - hint.get_width()//2,     HEIGHT//2 + 80))
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


def fade_to_black(screen, clock):
    for alpha in range(0, 256, 5):
        fade = pygame.Surface(screen.get_size())
        fade.fill((0, 0, 0))
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 4 — THE WATCHERS
# ─────────────────────────────────────────────────────────────────────────────

def run_level4(screen, clock, start_with_wrench=False,
               potion_inv=None, **kwargs):

    if potion_inv is None:
        potion_inv = PotionInventory()

    WIDTH, HEIGHT = screen.get_size()

    WHITE = (220, 220, 220)
    RED   = (200, 40, 40)
    MOON  = (190, 215, 255)

    # descent music — low and uneasy
    stop_music()
    try:
        play_music("assets/audio/moon_theme.ogg", loop=True, volume=0.4)
    except Exception:
        pass

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except Exception:
        font       = pygame.font.SysFont("courier", 20)
        font_small = pygame.font.SysFont("courier", 14)

    # ── SPRITES ──────────────────────────────────────────────────────
    player_sprites = AnimatedSprite(
        "assets/sprites/player.png", num_frames=4, frame_duration=8, scale=1)

    # placeholder figure used only for the brief crewmate apparition
    figure_sprite = AnimatedSprite(
        "assets/sprites/player.png", num_frames=4, frame_duration=10, scale=1)

    wrench_img = pygame.image.load("assets/sprites/wrench.png").convert_alpha()
    wrench_img = pygame.transform.scale(wrench_img, (24, 24))

    # ── LAYOUT — a vertical descent of three chambers ───────────────
    #   C1 Gallery (spawn)  →  C2 The Stacks (gauntlet)  →  C3 Antechamber (lift)
    ROOM1 = pygame.Rect(340,  90, 600, 150)   # top
    CORR1 = pygame.Rect(615, 240,  70,  70)
    ROOM2 = pygame.Rect(180, 310, 920, 160)   # wide middle
    CORR2 = pygame.Rect(615, 470,  70,  70)
    ROOM3 = pygame.Rect(340, 540, 600, 150)   # bottom
    all_rooms = [ROOM1, CORR1, ROOM2, CORR2, ROOM3]

    def in_walkable(rect):
        corners = [rect.topleft, rect.topright,
                   rect.bottomleft, rect.bottomright]
        return all(any(r.collidepoint(c) for r in all_rooms) for c in corners)

    # ── PLAYER ───────────────────────────────────────────────────────
    player_pos   = pygame.Vector2(ROOM1.x + 40, ROOM1.centery - 24)
    PLAYER_SIZE  = 48
    PLAYER_SPEED = 4
    health       = 100
    max_health   = 100

    # ── FLASHLIGHT ───────────────────────────────────────────────────
    FLASHLIGHT_RADIUS = 500
    CONE_ANGLE        = math.radians(45)
    darkness          = pygame.Surface((WIDTH, HEIGHT))
    glitch_intensity  = 0

    # ── WRENCH ───────────────────────────────────────────────────────
    has_wrench       = start_with_wrench
    wrench_on_ground = None
    wrenches         = []
    WRENCH_SPEED     = 10

    # ── POWER NODES (reused FuseBox) ─────────────────────────────────
    node_1    = FuseBox(ROOM1.x + 40,  ROOM1.y + 50)        # tutorial node
    node_2    = FuseBox(ROOM2.x + 30,  ROOM2.y + 30)        # far left of gauntlet
    node_3    = FuseBox(ROOM3.x + 40,     ROOM3.y + 60)     # deep in antechamber
    all_nodes = [node_1, node_2, node_3]

    # ── SHADES ───────────────────────────────────────────────────────
    shades = [
        Shade(ROOM2.x + 280, ROOM2.y + 60,  speed=1.71),
        Shade(ROOM2.x + 560, ROOM2.y + 70,  speed=1.8),
        Shade(ROOM3.x + 270, ROOM3.y + 50,  speed=1.62),
    ]

    # ── BOXES (cover / shadow lanes) ─────────────────────────────────
    stat_boxes = [
        StationaryBox(ROOM2.x + 200, ROOM2.y + 95, 70, 45),
        StationaryBox(ROOM2.x + 640, ROOM2.y + 95, 70, 45),
    ]
    mov_boxes = [
        MovableBox(ROOM2.x + 420, ROOM2.y + 60, 60, 45),
    ]
    room_bounds = (ROOM2.x, ROOM2.y, ROOM2.right, ROOM2.bottom)

    # ── EXIT (the cannon lift) ───────────────────────────────────────
    exit_door = pygame.Rect(ROOM1.right - 12, ROOM1.centery - 30, 18, 60)
    door_open = False

    # ── FALLING MOONLIGHT FLOOD ──────────────────────────────────────
    tide_active  = False
    tide_top  = ROOM3.bottom             # starts at screen bottom
    TIDE_RISE    = 0.45                  # px/frame the flood ascends
    TIDE_MIN_Y   = ROOM1.y               # how far down it ultimately reaches

    # ── DIALOGUE / EVENT FLAGS ───────────────────────────────────────
    intro_done    = False
    c2_event_done = False
    tide_warned   = False
    exit_done     = False

    # crewmate apparition
    glimpse_timer = 0
    GLIMPSE_POS   = (ROOM2.right - 90, ROOM2.y + 90)

    # ── SURFACE ──────────────────────────────────────────────────────
    game_surf = pygame.Surface((WIDTH, HEIGHT))

    running = True
    while running:

        pcx    = player_pos.x + PLAYER_SIZE // 2
        pcy    = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()
        angle  = math.atan2(my - pcy, mx - pcx)
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # ── OPENING DIALOGUE — the rule inverts ──────────────────────
        if not intro_done:
            intro_done = True
            screen.fill((0, 0, 0))
            run_dialogue(screen, clock, [
                ("The cannons are just below.",            RED),
                ("Keep moving. Don't stop.",               RED),
                ("...why is it so bright down here?",      WHITE),
                ("It doesn't matter. Keep your light up.", RED),
                ("There's something in the dark.",         WHITE),
                ("Shine your light on it. Like before.",   RED),
                ("...",                                    WHITE),
                ("Wait — when I look at it...",            WHITE),
                ("...it comes closer.",                    WHITE),
                ("DO AS I SAY.",                           RED),
                ("No.",                                    WHITE),
                ("Look away.",                             WHITE),
            ], black_bg=True)

        # ── ENTER C2 — crewmate glimpse + seed of doubt ──────────────
        if not c2_event_done and ROOM2.collidepoint(pcx, pcy):
            c2_event_done = True
            glimpse_timer = 90
            run_dialogue(screen, clock, [
                ("...did something just move?",             WHITE),
                ("There is no one else down here.",         RED),
                ("I saw a person. A crewmate.",             WHITE),
                ("They will try to stop you. Ignore them.", RED),
            ])

        # ── NEARBY NODE ──────────────────────────────────────────────
        active_node = None
        for i, nd in enumerate(all_nodes):
            if not nd.fixed and nd.is_near(pcx, pcy):
                active_node = i

        # ── EVENTS ───────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_result = run_pause(screen, clock, game_surf)
                    if pause_result == "restart":
                        return None
                    elif pause_result == "menu":
                        return "menu"

                if event.key == pygame.K_e and active_node is not None:
                    result = run_fuse_puzzle(screen, clock)
                    if result == "solved":
                        all_nodes[active_node].fixed = True

                if event.key == pygame.K_q:
                    health = potion_inv.use(health, max_health)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and has_wrench:
                    dxw = mx - pcx
                    dyw = my - pcy
                    dist = math.hypot(dxw, dyw)
                    if dist > 0:
                        has_wrench = False
                        wrenches.append({
                            "pos": pygame.Vector2(pcx, pcy),
                            "vel": pygame.Vector2(dxw/dist * WRENCH_SPEED,
                                                  dyw/dist * WRENCH_SPEED),
                            "life": 30,
                            "rotation": 0,
                        })

        # ── MOVEMENT (axis-separated, multi-room walkable) ───────────
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += PLAYER_SPEED

        moving = (dx != 0 or dy != 0)
        player_sprites.update(moving)

        # try X
        test = pygame.Rect(player_pos.x + dx, player_pos.y,
                           PLAYER_SIZE, PLAYER_SIZE)
        if in_walkable(test):
            nx, _ = test.x, None
            # block against stationary boxes
            for sb in stat_boxes:
                nx, _y = sb.blocks_player(nx, player_pos.y,
                                          PLAYER_SIZE, player_pos)
            player_pos.x = nx
        # try Y
        test = pygame.Rect(player_pos.x, player_pos.y + dy,
                           PLAYER_SIZE, PLAYER_SIZE)
        if in_walkable(test):
            ny = test.y
            for sb in stat_boxes:
                _x, ny = sb.blocks_player(player_pos.x, ny,
                                          PLAYER_SIZE, player_pos)
            player_pos.y = ny

        # push movable boxes
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)
        for mb in mov_boxes:
            if player_rect_cur.colliderect(mb.rect):
                old = (mb.rect.x, mb.rect.y)
                mb.push(dx, dy, player_rect_cur, room_bounds,
                        valid_rooms=all_rooms)
                # hard stop if box didn't move (wall behind it)
                if (mb.rect.x, mb.rect.y) == old:
                    if dx > 0: player_pos.x = mb.rect.left - PLAYER_SIZE
                    if dx < 0: player_pos.x = mb.rect.right
                    if dy > 0: player_pos.y = mb.rect.top - PLAYER_SIZE
                    if dy < 0: player_pos.y = mb.rect.bottom

        # recalc centre
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # ── SHADES UPDATE + CONTACT ──────────────────────────────────
        for sh in shades:
            sh.update(player_pos, PLAYER_SIZE, angle,
                      CONE_ANGLE, FLASHLIGHT_RADIUS, valid_rooms=all_rooms)
            if sh.get_rect().colliderect(player_rect_cur):
                health -= 0.84
                glitch_intensity = min(100, glitch_intensity + 4)

        # ── WRENCH UPDATE ────────────────────────────────────────────
        for w in wrenches[:]:
            w["pos"] += w["vel"]
            w["life"] -= 1
            w["rotation"] += 20
            wr = pygame.Rect(w["pos"].x - 5, w["pos"].y - 5, 10, 10)

            # hit a shade?
            struck = False
            for sh in shades:
                if sh.get_rect().colliderect(wr):
                    sh.stun()
                    struck = True
            in_bounds = any(r.collidepoint(w["pos"].x, w["pos"].y)
                            for r in all_rooms)
            if struck or not in_bounds or w["life"] <= 0:
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrenches.remove(w)

        if wrench_on_ground:
            gr = pygame.Rect(wrench_on_ground.x - 8,
                             wrench_on_ground.y - 8, 20, 20)
            if player_rect_cur.colliderect(gr):
                has_wrench = True
                wrench_on_ground = None

        # ── DOOR / TIDE TRIGGER ──────────────────────────────────────
        if all(nd.fixed for nd in all_nodes):
            if not door_open:
                door_open = True
            if not tide_active:
                tide_active = True

        if tide_active:
            tide_top = max(TIDE_MIN_Y, tide_top - TIDE_RISE)
            if not tide_warned:
                tide_warned = True
                run_dialogue(screen, clock, [
                    ("Power restored. The lift is live.", RED),
                    ("The light — it's falling —",        WHITE),
                    ("MOVE. Go down, now.",               RED),
                ])

        # ── MOONLIGHT DAMAGE (the tide) ──────────────────────────────
        taking_damage = tide_active and (pcy >= tide_top)
        if taking_damage:
            glitch_intensity = min(100, glitch_intensity + 3)
            health -= 0.3
        else:
            glitch_intensity = max(0, glitch_intensity - 4)
        health = max(0, health)

        # ── DEATH ────────────────────────────────────────────────────
        if health <= 0:
            run_death_screen(screen, clock)
            return None

        # ── EXIT ─────────────────────────────────────────────────────
        if door_open and player_rect_cur.colliderect(exit_door):
            if has_wrench and not exit_done:
                exit_done = True
                fade_to_black(screen, clock)
                screen.fill((0, 0, 0))
                run_dialogue(screen, clock, [
                    ("The lift's going down. Toward the guns.",      WHITE),
                    ("Good. You're almost there.",                   RED),
                    ("That crewmate... they weren't attacking me.",  WHITE),
                    ("They were warning me.",                        WHITE),
                    ("Lies. Keep going.",                            RED),
                    ("...I'm starting to wonder who's lying.",       WHITE),
                ], black_bg=True)
                stop_music()
                return "level5"

        # ─────────────────────────────────────────────────────────────
        # DRAW
        # ─────────────────────────────────────────────────────────────
        game_surf.fill((5, 5, 15))

        def draw_room(rect):
            pygame.draw.rect(game_surf, (15, 16, 25), rect)
            pygame.draw.rect(game_surf, (50, 55, 70), rect, 3)
            for gx in range(rect.x, rect.right, 50):
                pygame.draw.line(game_surf, (20, 22, 32),
                                 (gx, rect.y), (gx, rect.bottom))
            for gy in range(rect.y, rect.bottom, 50):
                pygame.draw.line(game_surf, (20, 22, 32),
                                 (rect.x, gy), (rect.right, gy))

        for room in all_rooms:
            draw_room(room)

        # boxes
        for sb in stat_boxes:
            sb.draw(game_surf, font_small)
        for mb in mov_boxes:
            mb.draw(game_surf, font_small)

        # power nodes
        for nd in all_nodes:
            nd.draw(game_surf, font_small)

        # exit lift
        door_color = (0, 200, 100) if door_open else (60, 80, 60)
        pygame.draw.rect(game_surf, door_color, exit_door)
        tag = "[LIFT]" if door_open else "[NO POWER]"
        tcol = (100, 255, 100) if door_open else (150, 150, 150)
        lbl = font_small.render(tag, True, tcol)
        game_surf.blit(lbl, (exit_door.x - lbl.get_width() - 5,
                             exit_door.centery - 8))

        # shades
        for sh in shades:
            sh.draw(game_surf)

        # crewmate apparition (brief)
        if glimpse_timer > 0:
            glimpse_timer -= 1
            figure_sprite.update(True)
            tmp = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            figure_sprite.draw(tmp, 0, 0)
            tmp.set_alpha(110)
            game_surf.blit(tmp, GLIMPSE_POS)

        # wrench on ground
        if wrench_on_ground:
            game_surf.blit(wrench_img,
                           (int(wrench_on_ground.x - 12),
                            int(wrench_on_ground.y - 12)))

        # flying wrenches
        for w in wrenches:
            rotated = pygame.transform.rotate(wrench_img, w["rotation"])
            rect = rotated.get_rect(center=(int(w["pos"].x), int(w["pos"].y)))
            game_surf.blit(rotated, rect)

        # falling moonlight flood — drawn after darkness so it's always visible
        if tide_active and tide_top < ROOM3.bottom:
            tide_surf = pygame.Surface((WIDTH, int(HEIGHT - tide_top)), pygame.SRCALPHA)
            tide_surf.fill((MOON[0], MOON[1], MOON[2], 90))
            game_surf.blit(tide_surf, (0, int(tide_top)))
            pygame.draw.line(game_surf, (230, 240, 255),
                             (0, int(tide_top)), (WIDTH, int(tide_top)), 2)
            
        # flashlight
        draw_flashlight(game_surf, darkness, pcx, pcy, angle,
                        CONE_ANGLE, FLASHLIGHT_RADIUS)

        # player
        player_sprites.draw(game_surf, int(player_pos.x), int(player_pos.y))

        # glitch
        if glitch_intensity > 0:
            apply_glitch(game_surf, glitch_intensity, WIDTH, HEIGHT)

        # prompts
        if active_node is not None:
            p = font.render("PRESS E TO RESTORE POWER", True, (200, 200, 100))
            game_surf.blit(p, (pcx - p.get_width()//2, pcy - 50))

        if any(sh.active for sh in shades):
            warn = font.render("LOOK AWAY", True, (200, 80, 80))
            game_surf.blit(warn, (pcx - warn.get_width()//2, pcy - 72))

        if door_open and player_rect_cur.colliderect(exit_door) \
                and not has_wrench:
            warn = font.render("[ FIND YOUR WRENCH BEFORE LEAVING ]",
                               True, (200, 80, 80))
            game_surf.blit(warn, (pcx - warn.get_width()//2, pcy - 70))

        # node counter
        fixed = sum(1 for nd in all_nodes if nd.fixed)
        cnt = font.render(f"POWER:  {fixed} / {len(all_nodes)}",
                          True, (160, 160, 200))
        game_surf.blit(cnt, (ROOM1.x, ROOM1.y - 34))

        screen.fill((0, 0, 0))
        screen.blit(game_surf, (0, 0))

        draw_hud(screen, font, health, max_health, glitch_intensity, has_wrench)
        potion_inv.draw(screen, font_small)

        pygame.display.flip()
        clock.tick(60)