import pygame
import sys
import math

from systems.lever import Lever
from systems.hud import draw_hud
from systems.boxes import StationaryBox
from systems.dialogue import run_dialogue
from systems.pause import run_pause
from systems.potion import PotionInventory
from systems.audio import stop_music
from entities.crewmate import Crewmate
from sprite_loader import AnimatedSprite


# ─────────────────────────────────────────────────────────────────────────────
# ENDING SCREENS
# ─────────────────────────────────────────────────────────────────────────────

def _crawl(screen, clock, lines):
    """Shared text-crawl renderer. lines = [(text, font, colour, delay_ms)]"""
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.wait(1000)

    y = HEIGHT // 2 - (len(lines) * 58) // 2
    for text, font, colour, delay in lines:
        rendered = font.render(text, True, colour)
        screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, y))
        pygame.display.flip()
        pygame.time.wait(delay)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        y += 58

    pygame.time.wait(4000)


def run_bad_ending(screen, clock):
    """The cannon fires. The moon wins. Earth is destroyed."""
    try:
        fb = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        fs = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
    except Exception:
        fb = pygame.font.SysFont("courier", 48, bold=True)
        fs = pygame.font.SysFont("courier", 24)

    _crawl(screen, clock, [
        ("The cannon fires.",                        fb, (180, 180, 180), 1400),
        ("The moon absorbs the energy.",             fs, (140, 140, 140), 1400),
        ("It grows.",                                fb, (200,  60,  60), 1400),
        ("The earth is the first to go.",            fs, (160,  60,  60), 1400),
        ("The crew never made it off the ship.",     fs, (120, 120, 120), 1400),
        ("Neither did you.",                         fs, (120, 120, 120), 1400),
        ("The moon got what it wanted.",             fb, (160,  30,  30), 1800),
    ])


def run_neutral_ending(screen, clock):
    """The player stands down. Ship is lost — but earth survives."""
    try:
        fb = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        fs = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
    except Exception:
        fb = pygame.font.SysFont("courier", 48, bold=True)
        fs = pygame.font.SysFont("courier", 24)

    _crawl(screen, clock, [
        ("You step back.",                           fb, (180, 180, 180), 1400),
        ("The ship is too far gone.",                fs, (140, 140, 140), 1400),
        ("The hull gives way.",                      fb, (180, 120,  60), 1400),
        ("But the moon never got what it wanted.",   fs, (120, 160, 120), 1400),
        ("Somewhere, far below, the earth turns on.",fs, (120, 180, 120), 1400),
        ("That will have to be enough.",             fb, (100, 200, 120), 1800),
    ])


def run_cannon_choice(screen, clock):
    """
    Crewmate's final plea + player choice.
    Returns "fire" or "standdown".
    """
    WIDTH, HEIGHT = screen.get_size()

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 28)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 18)
    except Exception:
        font       = pygame.font.SysFont("courier", 28)
        font_small = pygame.font.SysFont("courier", 18)

    # Final crewmate plea
    run_dialogue(screen, clock, [
        ("Please.",                                         (220, 100, 100)),
        ("You don't have to do this.",                      (220, 220, 220)),
        ("The moon fed you every lie you needed to hear.",  (220, 100, 100)),
        ("The cannon doesn't destroy it — it becomes it.",  (255,  60,  60)),
        ("Fire that thing and the earth dies with us.",     (220, 100, 100)),
        ("Is that what you want?",                          (220, 220, 220)),
        ("...",                                             (160, 160, 160)),
        ("Make your choice.",                               (200, 200, 200)),
    ], black_bg=True)

    # Choice screen
    options  = ["FIRE THE CANNON", "STAND DOWN"]
    selected = 0

    RED   = (200,  40,  40)
    WHITE = (220, 220, 220)
    DIM   = (100, 100, 100)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return "fire" if selected == 0 else "standdown"

        screen.fill((0, 0, 0))

        title = font.render("WHAT DO YOU DO?", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

        for i, opt in enumerate(options):
            col  = RED if i == 0 else (100, 220, 120)
            text = font.render(
                ("> " if i == selected else "  ") + opt,
                True, col if i == selected else DIM)
            screen.blit(text,
                        (WIDTH // 2 - text.get_width() // 2,
                         HEIGHT // 2 - 20 + i * 56))

        hint = font_small.render("W/S to choose   ENTER to confirm",
                                 True, (70, 70, 70))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 6
# ─────────────────────────────────────────────────────────────────────────────

def run_level6(screen, clock, potion_inv=None, **kwargs):

    if potion_inv is None:
        potion_inv = PotionInventory()

    WIDTH, HEIGHT = screen.get_size()

    stop_music()   # silence — let the tension breathe

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except Exception:
        font       = pygame.font.SysFont("courier", 20)
        font_small = pygame.font.SysFont("courier", 14)

    # ── ROOM ─────────────────────────────────────────────────────────
    ROOM_LEFT   = 290
    ROOM_TOP    = 120
    ROOM_RIGHT  = 990
    ROOM_BOTTOM = 600
    ROOM_W      = ROOM_RIGHT  - ROOM_LEFT   # 700
    ROOM_H      = ROOM_BOTTOM - ROOM_TOP    # 480
    ROOM_CX     = ROOM_LEFT + ROOM_W // 2   # 640
    ROOM_CY     = ROOM_TOP  + ROOM_H // 2   # 360

    valid_room = [pygame.Rect(ROOM_LEFT, ROOM_TOP, ROOM_W, ROOM_H)]

    # ── PLAYER ───────────────────────────────────────────────────────
    player_pos        = pygame.Vector2(ROOM_CX - 24, ROOM_BOTTOM - 100)
    PLAYER_SIZE       = 48
    PLAYER_SPEED      = 4
    health            = 100
    max_health        = 100
    player_stun_timer = 0

    player_sprite = AnimatedSprite(
        "assets/sprites/player.png",
        num_frames=4,
        frame_duration=8,
        scale=1
    )

    # ── PILLARS ───────────────────────────────────────────────────────
    # Centre pillar
    pillar_centre = StationaryBox(ROOM_CX - 35, ROOM_CY - 35, 70, 70)
    # Left and right mid-wall pillars only — top/bottom removed as they
    # overlap with the crewmate and player spawn positions
    pillar_left   = StationaryBox(ROOM_LEFT  + 70, ROOM_CY - 20, 40, 40)
    pillar_right  = StationaryBox(ROOM_RIGHT - 110, ROOM_CY - 20, 40, 40)

    all_pillars = [pillar_centre, pillar_left, pillar_right]

    # ── LEVERS (four corners, inset from walls) ───────────────────────
    levers = [
        Lever(ROOM_LEFT  + 40,   ROOM_TOP    + 40),   # top-left
        Lever(ROOM_RIGHT - 88,   ROOM_TOP    + 40),   # top-right
        Lever(ROOM_LEFT  + 40,   ROOM_BOTTOM - 88),   # bottom-left
        Lever(ROOM_RIGHT - 88,   ROOM_BOTTOM - 88),   # bottom-right
    ]

    # ── CANNON PLACEHOLDER ────────────────────────────────────────────
    cannon_rect     = pygame.Rect(ROOM_CX - 50, ROOM_TOP + 10, 100, 50)
    CANNON_NEAR_RAD = 70
    cannon_ready    = False   # set True once all levers are fixed

    # ── CREWMATE ─────────────────────────────────────────────────────
    crewmate = Crewmate(ROOM_CX - 24, ROOM_TOP + 80)

    # ── WRENCH ────────────────────────────────────────────────────────
    WRENCH_SPEED     = 10
    wrench_img       = pygame.image.load(
                           "assets/sprites/wrench.png").convert_alpha()
    wrench_img       = pygame.transform.scale(wrench_img, (24, 24))
    has_wrench       = True
    wrenches         = []
    wrench_on_ground = None

    # ── GAME SURFACE (for pause snapshot) ────────────────────────────
    game_surf = pygame.Surface((WIDTH, HEIGHT))

    # ── OPENING DIALOGUE ─────────────────────────────────────────────
    run_dialogue(screen, clock, [
        ("Stop.",                                          (220, 100, 100)),
        ("I know what you're about to do.",                (220, 220, 220)),
        ("The voice that guided you — that was the moon.", (220, 100, 100)),
        ("The cannon doesn't destroy it.",                 (220, 100, 100)),
        ("It feeds it.",                                   (255,  60,  60)),
        ("If you fire that cannon, we all die.",           (220, 100, 100)),
        ("...",                                            (160, 160, 160)),
        ("I can't let you do this.",                       (220, 220, 220)),
    ], black_bg=True)

    # ── MAIN LOOP ─────────────────────────────────────────────────────
    running = True
    while running:

        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        mx, my = pygame.mouse.get_pos()

        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # Check all levers fixed
        cannon_ready = all(lv.fixed for lv in levers)

        # Nearby lever (unfixed, within range)
        near_lever = None
        for lv in levers:
            if not lv.fixed and lv.is_near(pcx, pcy):
                near_lever = lv
                break

        # Near cannon (only when all levers fixed)
        near_cannon = (
            cannon_ready and
            math.hypot(pcx - cannon_rect.centerx,
                       pcy - cannon_rect.centery) < CANNON_NEAR_RAD
        )

        # ── events ───────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = run_pause(screen, clock, game_surf)
                    if result == "continue":
                        pass
                    elif result == "restart":
                        return None
                    elif result == "menu":
                        return "menu"

                if event.key == pygame.K_q:
                    health = potion_inv.use(health, max_health)

                # Cannon — single press E triggers choice dialogue
                if event.key == pygame.K_e and near_cannon \
                        and player_stun_timer == 0:
                    choice = run_cannon_choice(screen, clock)
                    if choice == "fire":
                        run_bad_ending(screen, clock)
                    else:
                        run_neutral_ending(screen, clock)
                    return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and has_wrench:
                    dx_w = mx - pcx
                    dy_w = my - pcy
                    dist = math.hypot(dx_w, dy_w)
                    if dist > 0:
                        has_wrench = False
                        wrenches.append({
                            "pos":      pygame.Vector2(pcx, pcy),
                            "vel":      pygame.Vector2(
                                            dx_w / dist * WRENCH_SPEED,
                                            dy_w / dist * WRENCH_SPEED),
                            "life":     40,
                            "rotation": 0,
                        })

        keys = pygame.key.get_pressed()

        # ── player stun tick ─────────────────────────────────────────
        if player_stun_timer > 0:
            player_stun_timer -= 1

        # ── lever hold mechanic ──────────────────────────────────────
        holding_lever = (
            player_stun_timer == 0 and
            keys[pygame.K_e] and
            near_lever is not None
        )
        for lv in levers:
            lv.update(holding_lever and lv is near_lever)

        # ── player movement ───────────────────────────────────────────
        dx = dy = 0
        if player_stun_timer == 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= PLAYER_SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += PLAYER_SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= PLAYER_SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += PLAYER_SPEED

        moving = dx != 0 or dy != 0
        player_sprite.update(moving)

        new_x = player_pos.x + dx
        new_y = player_pos.y + dy

        new_x = max(ROOM_LEFT, min(ROOM_RIGHT  - PLAYER_SIZE, new_x))
        new_y = max(ROOM_TOP,  min(ROOM_BOTTOM - PLAYER_SIZE, new_y))

        for p in all_pillars:
            new_x, new_y = p.blocks_player(new_x, new_y, PLAYER_SIZE,
                                            player_pos)

        player_pos.x = new_x
        player_pos.y = new_y

        pcx = player_pos.x + PLAYER_SIZE // 2
        pcy = player_pos.y + PLAYER_SIZE // 2
        player_rect_cur = pygame.Rect(
            player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

        # ── crewmate ─────────────────────────────────────────────────
        obstacle_rects = [p.rect for p in all_pillars]
        crewmate.update(
            player_pos, PLAYER_SIZE, levers,
            valid_rooms=valid_room,
            obstacle_rects=obstacle_rects
        )
        has_fixed = any(lv.fixed for lv in levers)
        if crewmate.try_stun_player(player_pos, PLAYER_SIZE,
                                    has_fixed_levers=has_fixed):
            player_stun_timer = 120

        # ── wrenches ─────────────────────────────────────────────────
        for w in wrenches[:]:
            w["pos"]      += w["vel"]
            w["life"]     -= 1
            w["rotation"] += 20
            wr        = pygame.Rect(w["pos"].x, w["pos"].y, 10, 10)
            in_bounds = (ROOM_LEFT <= w["pos"].x <= ROOM_RIGHT and
                         ROOM_TOP  <= w["pos"].y <= ROOM_BOTTOM)
            if wr.colliderect(crewmate.get_rect()):
                crewmate.stun(180)
                wrench_on_ground = pygame.Vector2(w["pos"])
                wrenches.remove(w)
                continue
            if not in_bounds or w["life"] <= 0:
                wrench_on_ground = pygame.Vector2(
                    max(ROOM_LEFT, min(ROOM_RIGHT,  w["pos"].x)),
                    max(ROOM_TOP,  min(ROOM_BOTTOM, w["pos"].y)))
                wrenches.remove(w)
                continue

        if wrench_on_ground:
            gr = pygame.Rect(wrench_on_ground.x, wrench_on_ground.y, 16, 16)
            if player_rect_cur.colliderect(gr):
                has_wrench       = True
                wrench_on_ground = None

        # ── DRAW ──────────────────────────────────────────────────────
        game_surf.fill((30, 32, 40))

        # Floor grid
        for gx in range(ROOM_LEFT, ROOM_RIGHT, 60):
            pygame.draw.line(game_surf, (38, 40, 52),
                             (gx, ROOM_TOP), (gx, ROOM_BOTTOM))
        for gy in range(ROOM_TOP, ROOM_BOTTOM, 60):
            pygame.draw.line(game_surf, (38, 40, 52),
                             (ROOM_LEFT, gy), (ROOM_RIGHT, gy))

        # Room walls
        pygame.draw.rect(game_surf, (70, 75, 95),
                         (ROOM_LEFT, ROOM_TOP, ROOM_W, ROOM_H), 4)

        # Cannon placeholder
        cannon_col = (80, 180, 80) if cannon_ready else (80, 80, 80)
        pygame.draw.rect(game_surf, cannon_col, cannon_rect)
        pygame.draw.rect(game_surf, (120, 120, 120), cannon_rect, 2)
        c_label = font_small.render("CANNON", True, (200, 200, 200))
        game_surf.blit(c_label, (
            cannon_rect.centerx - c_label.get_width() // 2,
            cannon_rect.centery - c_label.get_height() // 2))

        # Pillars
        for p in all_pillars:
            p.draw(game_surf, font_small)

        # Levers
        for lv in levers:
            lv.draw(game_surf, font_small)

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

        # Crewmate
        crewmate.draw(game_surf)

        # Player
        player_sprite.draw(game_surf, int(player_pos.x), int(player_pos.y))

        # ── prompts ───────────────────────────────────────────────────
        if near_lever is not None and player_stun_timer == 0:
            prompt = font.render("HOLD E TO ACTIVATE", True, (200, 200, 100))
            game_surf.blit(prompt,
                           (pcx - prompt.get_width() // 2, pcy - 60))

        if near_cannon and player_stun_timer == 0:
            prompt = font.render("PRESS E — FIRE CANNON", True, (100, 255, 100))
            game_surf.blit(prompt,
                           (pcx - prompt.get_width() // 2, pcy - 60))

        if player_stun_timer > 0:
            stun_msg = font.render("STUNNED", True, (180, 100, 255))
            game_surf.blit(stun_msg,
                           (pcx - stun_msg.get_width() // 2, pcy - 60))

        # Lever count
        fixed_count = sum(1 for lv in levers if lv.fixed)
        count_text  = font.render(
            f"CANNON CHARGE:  {fixed_count} / {len(levers)}",
            True, (160, 160, 200))
        game_surf.blit(count_text, (ROOM_LEFT + 10, ROOM_TOP - 30))

        screen.fill((0, 0, 0))
        screen.blit(game_surf, (0, 0))

        draw_hud(screen, font, health, max_health, 0, has_wrench)
        potion_inv.draw(screen, font_small)

        pygame.display.flip()
        clock.tick(60)
