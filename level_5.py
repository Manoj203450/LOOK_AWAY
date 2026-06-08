# Pieter lvl 5: THE THRESHOLD
import pygame
import sys
import math

from systems.flashlight     import draw_flashlight
from systems.moonlight      import apply_glitch
from systems.hud            import draw_hud, set_fps
from systems.boxes          import StationaryBox, MovableBox
from systems.fuse_puzzle    import FuseBox, run_fuse_puzzle
from systems.potion         import PotionInventory
from systems.dialogue       import run_dialogue
from systems.pause          import run_pause
from systems.audio          import play_music, stop_music
from entities.shade         import Shade
from entities.weeping_angel import WeepingAngel
from entities.enemy         import Enemy
from entities.crewmate      import Crewmate
from sprite_loader          import AnimatedSprite


# Helpers
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
    t1 = font_big.render("YOU LOOKED.",               True, (180, 30,  30))
    t2 = font_small.render("the threshold took you.", True, (100, 100, 100))
    t3 = font_small.render("press any key to retry",  True, ( 60,  60,  60))
    screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 80))
    screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 10))
    screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 80))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
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


# Start point
def run_level5(screen, clock, start_with_wrench=True,
               potion_inv=None, **kwargs):
    """
    Level 5 — THE THRESHOLD.
    Called by main.py's play_level() wrapper.
    **kwargs absorbs 'restart_music' without error.
    """
    if potion_inv is None:
        potion_inv = PotionInventory()

    WIDTH, HEIGHT = screen.get_size()

    WHITE = (220, 220, 220)
    RED   = (200,  40,  40)
    MOON  = (190, 215, 255)

    # Lvl music
    stop_music()
    try:
        play_music("assets/audio/lvl5.ogg", loop=True, volume=0.4)
    except Exception:
        try:
            play_music("assets/audio/moon_theme.ogg", loop=True, volume=0.4)
        except Exception:
            pass

    # Fonts
    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except Exception:
        font       = pygame.font.SysFont("courier", 20)
        font_small = pygame.font.SysFont("courier", 14)

    # Sprites
    player_sprites = AnimatedSprite(
        "assets/sprites/player.png", num_frames=4, frame_duration=8, scale=1)

    wrench_img = pygame.image.load("assets/sprites/wrench.png").convert_alpha()
    wrench_img = pygame.transform.scale(wrench_img, (24, 24))

    # Room layout
    ROOM_A  = pygame.Rect( 60,  70, 400, 200) # top-left
    ROOM_B  = pygame.Rect(820,  70, 400, 200) # top-right
    CORR_AB = pygame.Rect(460, 110, 360, 100) # horizontal corridor A↔B
    ROOM_C  = pygame.Rect( 60, 390, 1160, 250) # bottom
    CORR_AC = pygame.Rect( 90, 270,  100, 120) # left vertical A↔C
    CORR_BC = pygame.Rect(1090, 270, 100, 120) # right vertical B↔C

    all_rooms = [ROOM_A, ROOM_B, CORR_AB, ROOM_C, CORR_AC, CORR_BC]

    def in_walkable(rect):
        """True when all four corners of rect are inside some room."""
        corners = [rect.topleft, rect.topright,
                   rect.bottomleft, rect.bottomright]
        return all(any(r.collidepoint(c) for r in all_rooms) for c in corners)

    # Player
    player_pos   = pygame.Vector2(ROOM_A.x + 40, ROOM_A.centery - 24)
    PLAYER_SIZE  = 48
    PLAYER_SPEED = 4
    health       = 100
    max_health   = 100
    player_stun  = 0

    # The light
    FLASHLIGHT_RADIUS = 500
    CONE_ANGLE        = math.radians(45)
    darkness          = pygame.Surface((WIDTH, HEIGHT))
    glitch_intensity  = 0

    # Wrench
    has_wrench       = start_with_wrench
    wrench_on_ground = None
    wrenches         = []
    WRENCH_SPEED     = 10

    #   fuse_1  Room A, always available
    #   fuse_2  Room B, always available
    #   fuse_3  Room B, always available
    #   fuse_4  Room C, ORDER-LOCKED: fix 1-2-3 first
    node_1    = FuseBox(ROOM_A.x + 40,  ROOM_A.y + 50)
    node_2    = FuseBox(ROOM_B.x + 50,  ROOM_B.y + 40)
    node_3    = FuseBox(ROOM_B.right - 96, ROOM_B.y + 110)
    node_4    = FuseBox(ROOM_C.right - 120, ROOM_C.y + 100)
    all_nodes = [node_1, node_2, node_3, node_4]

    # Moonlight circles
    moon_circles = [
        (ROOM_A.centerx,       ROOM_A.centery,       50),
        (ROOM_B.x + 80,        ROOM_B.y + 80,        55),
        (ROOM_B.right - 80,    ROOM_B.centery,       45),
        (ROOM_C.x + 150,       ROOM_C.centery,       60),
        (ROOM_C.centerx - 100, ROOM_C.centery + 20,  55),
        (ROOM_C.right - 200,   ROOM_C.centery - 10,  50),
    ]

    # Boxes
    stat_boxes = [
        StationaryBox(ROOM_A.x + 140, ROOM_A.y + 10,  55, 45),
        StationaryBox(ROOM_B.x + 160, ROOM_B.y + 10,  55, 45),
        StationaryBox(ROOM_C.x + 240, ROOM_C.y + 10,  55, 45),
        StationaryBox(ROOM_C.x + 650, ROOM_C.bottom - 85, 55, 45),
    ]
    mov_boxes = [
        MovableBox(ROOM_A.x + 240, ROOM_A.centery - 10, 55, 45),
        MovableBox(ROOM_B.x + 260, ROOM_B.centery - 10, 55, 45),
        MovableBox(ROOM_C.x + 420, ROOM_C.y + 80,       55, 45),
    ]
    room_c_bounds = (ROOM_C.x, ROOM_C.y, ROOM_C.right, ROOM_C.bottom)

    # Room A, Worshipper (patrol the corners, chase on sight)
    enemy_a = Enemy(ROOM_A.centerx, ROOM_A.centery)
    enemy_a.patrol_points = [
        pygame.Vector2(ROOM_A.x + 60,      ROOM_A.y + 30),
        pygame.Vector2(ROOM_A.right - 60,  ROOM_A.y + 30),
        pygame.Vector2(ROOM_A.right - 60,  ROOM_A.bottom - 30),
        pygame.Vector2(ROOM_A.x + 60,      ROOM_A.bottom - 30),
    ]

    # Room B,
    #   WeepingAngel : frozen in flashlight
    #   Shade : moves in flashlight
    angel_b = WeepingAngel(ROOM_B.x + 60,     ROOM_B.y + 30)
    shade_b = Shade(ROOM_B.right - 108,        ROOM_B.y + 50, speed=2.0)

    # Room C, second shade + second worshipper
    shade_c = Shade(ROOM_C.x + 350, ROOM_C.centery - 20, speed=1.8)
    enemy_c = Enemy(ROOM_C.centerx,  ROOM_C.centery)
    enemy_c.patrol_points = [
        pygame.Vector2(ROOM_C.x + 80,   ROOM_C.y + 40),
        pygame.Vector2(ROOM_C.x + 400,  ROOM_C.y + 40),
        pygame.Vector2(ROOM_C.x + 400,  ROOM_C.bottom - 40),
        pygame.Vector2(ROOM_C.x + 80,   ROOM_C.bottom - 40),
    ]

    # Crewmate, spawns once all 4 nodes are fixed (room C)
    crewmate        = None
    crewmate_active = False
    crewmate_spoken = False

    # Visual-only glimpse flicker when entering room B
    glimpse_timer = 0
    GLIMPSE_POS   = (ROOM_B.centerx - 24, ROOM_B.bottom - 60)

    # Exit door
    exit_door = pygame.Rect(ROOM_C.right - 12, ROOM_C.centery - 30, 18, 60)
    door_open = False

    # Moonlight flood
    tide_active = False
    tide_top    = float(ROOM_C.bottom) # starts at room C floor, rises up
    TIDE_RISE   = 0.67
    TIDE_MIN_Y  = float(ROOM_A.y)

    # Event flags
    intro_done     = False
    room_b_entered = False
    tide_warned    = False
    exit_done      = False

    # Draw surface
    game_surf = pygame.Surface((WIDTH, HEIGHT))

    # Main loop
    running = True
    while running:

        pcx    = player_pos.x + PLAYER_SIZE // 2
        pcy    = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()
        angle  = math.atan2(my - pcy, mx - pcx)
        player_rect = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # Opening dialogue
        if not intro_done:
            intro_done = True
            screen.fill((0, 0, 0))
            run_dialogue(screen, clock, [
                ("Keep moving. The cannon is close.",          RED),
                ("...something is different here.",            WHITE),
                ("Don't think about it. Keep going.",          RED),
                ("The shadows. They're moving toward light.",  WHITE),
                ("Look away from them. Use your light wisely.", RED),
                ("...and the thing in the dark room?",         WHITE),
                ("Shine on it. Like before.",                  RED),
                ("What if shining on it wakes something else?", WHITE),
                ("JUST KEEP MOVING.",                          RED),
            ], black_bg=True)

        # ROOM B EVENT, glimpse of the crewmate
        if not room_b_entered and ROOM_B.collidepoint(pcx, pcy):
            room_b_entered = True
            glimpse_timer  = 90
            run_dialogue(screen, clock, [
                ("...there's someone in here.",               WHITE),
                ("There is no one. You're imagining things.", RED),
                ("They looked right at me.",                  WHITE),
                ("IGNORE THEM. FIX THE NODES.",               RED),
            ])

        # FIND NEAREST INTERACTABLE NODE
        active_node = None
        for i, nd in enumerate(all_nodes):
            if not nd.fixed and nd.is_near(pcx, pcy):
                if i == 3 and not all(all_nodes[j].fixed for j in range(3)):
                    continue
                active_node = i

        # EVENT QUEUE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

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
                            "pos":      pygame.Vector2(pcx, pcy),
                            "vel":      pygame.Vector2(dxw / dist * WRENCH_SPEED,
                                                       dyw / dist * WRENCH_SPEED),
                            "life":     60,
                            "rotation": 0,
                        })

        # PLAYER MOVEMENT
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if player_stun == 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= PLAYER_SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += PLAYER_SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= PLAYER_SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += PLAYER_SPEED
        else:
            player_stun -= 1

        moving = (dx != 0 or dy != 0)
        player_sprites.update(moving)

        test_x = pygame.Rect(player_pos.x + dx, player_pos.y,
                             PLAYER_SIZE, PLAYER_SIZE)
        if in_walkable(test_x):
            nx = player_pos.x + dx
            for sb in stat_boxes:
                nx, _ = sb.blocks_player(nx, player_pos.y,
                                         PLAYER_SIZE, player_pos)
            player_pos.x = nx

        test_y = pygame.Rect(player_pos.x, player_pos.y + dy,
                             PLAYER_SIZE, PLAYER_SIZE)
        if in_walkable(test_y):
            ny = player_pos.y + dy
            for sb in stat_boxes:
                _, ny = sb.blocks_player(player_pos.x, ny,
                                         PLAYER_SIZE, player_pos)
            player_pos.y = ny

        # Push movable boxes (Room C only)
        player_rect = pygame.Rect(player_pos.x, player_pos.y,
                                  PLAYER_SIZE, PLAYER_SIZE)
        for mb in mov_boxes:
            if player_rect.colliderect(mb.rect):
                old = (mb.rect.x, mb.rect.y)
                mb.push(dx, dy, player_rect, room_c_bounds,
                        valid_rooms=all_rooms)
                if (mb.rect.x, mb.rect.y) == old:
                    if dx > 0: player_pos.x = mb.rect.left  - PLAYER_SIZE
                    if dx < 0: player_pos.x = mb.rect.right
                    if dy > 0: player_pos.y = mb.rect.top   - PLAYER_SIZE
                    if dy < 0: player_pos.y = mb.rect.bottom

        # Recalculate after movement
        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect = pygame.Rect(player_pos.x, player_pos.y,
                                  PLAYER_SIZE, PLAYER_SIZE)

        # ENEMY AI
        enemy_a.update(player_pos, PLAYER_SIZE, valid_rooms=all_rooms)
        angel_b.update(player_pos, PLAYER_SIZE, angle,
                       CONE_ANGLE, FLASHLIGHT_RADIUS, valid_rooms=all_rooms)
        shade_b.update(player_pos, PLAYER_SIZE, angle,
                       CONE_ANGLE, FLASHLIGHT_RADIUS, valid_rooms=all_rooms)
        shade_c.update(player_pos, PLAYER_SIZE, angle,
                       CONE_ANGLE, FLASHLIGHT_RADIUS, valid_rooms=all_rooms)
        enemy_c.update(player_pos, PLAYER_SIZE, valid_rooms=all_rooms)

        if crewmate_active and crewmate is not None:
            crewmate.update(player_pos, PLAYER_SIZE,
                            [],
                            valid_rooms=all_rooms)

        # ENEMY CONTACT DAMAGE
        # Worshippers
        for ent in [enemy_a, enemy_c]:
            if (getattr(ent, "state", "") != "stunned"
                    and player_rect.colliderect(ent.get_rect())):
                health          -= 0.6
                glitch_intensity = min(100, glitch_intensity + 3)

        # Weeping Angel
        if not angel_b.frozen and player_rect.colliderect(angel_b.get_rect()):
            health = 0

        # Shades
        for shade in [shade_b, shade_c]:
            if (shade.stun_timer == 0
                    and player_rect.colliderect(shade.get_rect())):
                health          -= 0.84
                glitch_intensity = min(100, glitch_intensity + 4)

        # Crewmate
        if crewmate_active and crewmate is not None:
            if crewmate.try_stun_player(player_pos, PLAYER_SIZE,
                                        has_fixed_levers=False):
                player_stun      = 120
                health          -= 8
                glitch_intensity = min(100, glitch_intensity + 20)

        # WRENCH UPDATE
        for w in wrenches[:]:
            w["pos"]      += w["vel"]
            w["life"]     -= 1
            w["rotation"] += 20
            wr = pygame.Rect(w["pos"].x - 5, w["pos"].y - 5, 10, 10)

            struck     = False
            all_stun_targets = []
            if crewmate_active and crewmate is not None:
                all_stun_targets.append(crewmate)
            all_stun_targets += [enemy_a, shade_b, shade_c, enemy_c]

            for ent in all_stun_targets:
                if ent.get_rect().colliderect(wr):
                    ent.stun()

                    if ent is crewmate and not crewmate_spoken:
                        crewmate_spoken = True
                        run_dialogue(screen, clock, [
                            ("Please.",                                       WHITE),
                            ("Stop.",                                         WHITE),
                            ("The cannon doesn't destroy the moon.",          WHITE),
                            ("They'll say anything. Push through.",           RED),
                            ("It FEEDS it. Everything the Voice told you—",   WHITE),
                            ("LIES. ALL LIES. GO.",                           RED),
                            ("...",                                           WHITE),
                            ("(His eyes are clear. He's not corrupted.)",     WHITE),
                            ("(He's just afraid.)",                           WHITE),
                        ], black_bg=True)
                        door_open = True

                    struck = True
                    break

            # Stun weeping angel
            if not struck and angel_b.get_rect().colliderect(wr):
                angel_b.stun() if hasattr(angel_b, "stun") else None
                struck = True

            in_bounds = any(r.collidepoint(w["pos"].x, w["pos"].y)
                            for r in all_rooms)
            if struck or not in_bounds or w["life"] <= 0:
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrenches.remove(w)

        # Pick wrench up from ground
        if wrench_on_ground:
            gr = pygame.Rect(wrench_on_ground.x - 8,
                             wrench_on_ground.y - 8, 20, 20)
            if player_rect.colliderect(gr):
                has_wrench       = True
                wrench_on_ground = None

        # DOOR or FLOOD TRIGGER
        all_fixed = all(nd.fixed for nd in all_nodes)

        # When all 4 nodes are fixed, start flood + spawn crewmate
        if all_fixed and not tide_active:
            tide_active = True

        if tide_active and not tide_warned:
            tide_warned = True
            run_dialogue(screen, clock, [
                ("Power restored. Something changed.",  WHITE),
                ("The light — it's flooding —",         WHITE),
                ("MOVE. Get to the lift. NOW.",          RED),
                ("...and there's someone blocking it.", WHITE),
                ("DO NOT STOP.",                        RED),
            ])
            # Spawn crewmate at left side of Room C
            if crewmate is None:
                try:
                    crewmate        = Crewmate(ROOM_C.right - 105,
                                               ROOM_C.centery - 24)
                    crewmate_active = True
                except Exception:
                    # crewmate sprite missing, door opens automatically
                    door_open = True

        # If no crewmate could spawn, open door immediately
        if all_fixed and crewmate is None:
            door_open = True

        # FLOOD RISE
        if tide_active:
            tide_top = max(TIDE_MIN_Y, tide_top - TIDE_RISE)

        # MOONLIGHT CIRCLE DAMAGE
        for (cx, cy, r) in moon_circles:
            if math.hypot(pcx - cx, pcy - cy) < r:
                health          -= 0.3
                glitch_intensity = min(100, glitch_intensity + 2)

        # FLOOD DAMAGE
        taking_flood = tide_active and (pcy >= tide_top)
        if taking_flood:
            health          -= 0.3
            glitch_intensity = min(100, glitch_intensity + 3)
        else:
            glitch_intensity = max(0, glitch_intensity - 4)

        health = max(0, health)

        # DEATH CHECK
        if health <= 0:
            run_death_screen(screen, clock)
            return None

        # EXIT CHECK
        if door_open and player_rect.colliderect(exit_door):
            if has_wrench and not exit_done:
                exit_done = True
                fade_to_black(screen, clock)
                screen.fill((0, 0, 0))
                run_dialogue(screen, clock, [
                    ("The lift is right there.",                 WHITE),
                    ("Go. Don't look back.",                     RED),
                    ("That crewmate... he knew the truth.",      WHITE),
                    ("He was trying to save you, not stop you.", WHITE),
                    ("KEEP. MOVING.",                            RED),
                    ("...what have I done?",                     WHITE),
                ], black_bg=True)
                stop_music()
                return "level6"

        # Glimpse timer decay
        if glimpse_timer > 0:
            glimpse_timer -= 1

        # DRAW PHASE
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

        # Moonlight circles (translucent glow)
        for (cx, cy, r) in moon_circles:
            ml = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ml, (MOON[0], MOON[1], MOON[2], 80), (r, r), r)
            game_surf.blit(ml, (cx - r, cy - r))

        # Boxes
        for sb in stat_boxes:
            sb.draw(game_surf, font_small)
        for mb in mov_boxes:
            mb.draw(game_surf, font_small)

        # Power nodes
        for nd in all_nodes:
            nd.draw(game_surf, font_small)

        # Exit lift
        door_color = (0, 200, 100) if door_open else (60, 80, 60)
        pygame.draw.rect(game_surf, door_color, exit_door)
        tag  = "[LIFT]" if door_open else "[NO POWER]"
        tcol = (100, 255, 100) if door_open else (150, 150, 150)
        lbl  = font_small.render(tag, True, tcol)
        game_surf.blit(lbl, (exit_door.x - lbl.get_width() - 5,
                             exit_door.centery - 8))

        # Enemies
        enemy_a.draw(game_surf)
        angel_b.draw(game_surf)
        shade_b.draw(game_surf)
        shade_c.draw(game_surf)
        enemy_c.draw(game_surf)

        if crewmate_active and crewmate is not None:
            crewmate.draw(game_surf)

        # Crewmate glimpse flicker (silhouette in Room B on first entry)
        if glimpse_timer > 0 and glimpse_timer % 10 < 7:
            tmp = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(tmp, (130, 130, 200, 100), (0, 0, PLAYER_SIZE, PLAYER_SIZE))
            game_surf.blit(tmp, GLIMPSE_POS)

        # Wrench on ground
        if wrench_on_ground:
            game_surf.blit(wrench_img,
                           (int(wrench_on_ground.x - 12),
                            int(wrench_on_ground.y - 12)))

        # Flying wrenches
        for w in wrenches:
            rotated = pygame.transform.rotate(wrench_img, w["rotation"])
            rect    = rotated.get_rect(
                          center=(int(w["pos"].x), int(w["pos"].y)))
            game_surf.blit(rotated, rect)

        # Moonlight flood
        if tide_active and tide_top < ROOM_C.bottom:
            tide_h    = int(HEIGHT - tide_top)
            tide_surf = pygame.Surface((WIDTH, tide_h), pygame.SRCALPHA)
            tide_surf.fill((MOON[0], MOON[1], MOON[2], 90))
            game_surf.blit(tide_surf, (0, int(tide_top)))
            pygame.draw.line(game_surf, (230, 240, 255),
                             (0, int(tide_top)), (WIDTH, int(tide_top)), 2)

        # Flashlight darkness overlay
        draw_flashlight(game_surf, darkness, pcx, pcy, angle,
                        CONE_ANGLE, FLASHLIGHT_RADIUS)

        # Player drawn AFTER flashlight (always visible)
        player_sprites.draw(game_surf, int(player_pos.x), int(player_pos.y))

        # Glitch / scanline effect
        if glitch_intensity > 0:
            apply_glitch(game_surf, glitch_intensity, WIDTH, HEIGHT)

        # PROMPTS
        if active_node is not None:
            p = font.render("PRESS E TO RESTORE POWER", True, (200, 200, 100))
            game_surf.blit(p, (pcx - p.get_width() // 2, pcy - 50))

        # Order-lock hint when near node_4 too early
        if (not all_nodes[3].fixed
                and not all(all_nodes[j].fixed for j in range(3))
                and all_nodes[3].is_near(pcx, pcy)):
            hint = font_small.render(
                "restore the other nodes first", True, (180, 120, 60))
            game_surf.blit(hint, (pcx - hint.get_width() // 2, pcy - 70))

        # Shade active warning
        if any(s.active for s in [shade_b, shade_c]):
            warn = font.render("LOOK AWAY", True, (200, 80, 80))
            game_surf.blit(warn, (pcx - warn.get_width() // 2, pcy - 72))

        # Wrench requirement before exiting
        if door_open and player_rect.colliderect(exit_door) and not has_wrench:
            warn = font.render("[ FIND YOUR WRENCH FIRST ]",
                               True, (200, 80, 80))
            game_surf.blit(warn, (pcx - warn.get_width() // 2, pcy - 70))

        # COMPOSITE TO SCREEN
        screen.fill((0, 0, 0))
        screen.blit(game_surf, (0, 0))

        set_fps(clock.get_fps())
        draw_hud(screen, font, health, max_health, glitch_intensity, has_wrench)
        potion_inv.draw(screen, font_small)

        # Node counter
        fixed_count = sum(1 for nd in all_nodes if nd.fixed)
        cnt = font.render(f"POWER:  {fixed_count} / {len(all_nodes)}",
                          True, (160, 160, 200))
        screen.blit(cnt, (WIDTH - cnt.get_width() - 20, 20))

        pygame.display.flip()
        clock.tick(60)
