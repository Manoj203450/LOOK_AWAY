import pygame
from sprite_loader import AnimatedSprite


class Crewmate:
    """
    Final-level antagonist. A crewmate who knows the truth about the cannon
    and is trying to stop the player from activating it.

    Behaviour:
      - "chase"    : moves toward the player and stuns on contact
      - "sabotage" : moves toward the nearest active lever/fusebox and
                     spends SABOTAGE_DURATION frames disabling it
      - "stunned"  : frozen after being hit by a thrown wrench

    Speed scales with how many levers are currently fixed — goes up when
    the player fixes one, back down when the crewmate sabotages one.

    Works with any object that has  .fixed (bool)  and  .rect (pygame.Rect),
    so it is compatible with both FuseBox and the Level 6 Lever class.

    NOTE: sprite is using player.png as a placeholder.
          Replace "assets/sprites/player.png" with the crewmate sheet
          once the asset is ready.
    """

    BASE_SPEED        = 1.6   # starting speed
    SPEED_PER_FIX     = 0.6   # added per currently-fixed lever (increased)
    SABOTAGE_RADIUS   = 60    # px from lever centre to start the countdown
    SABOTAGE_DURATION = 120   # frames to disable a lever (2 s at 60 fps)
    STUN_COOLDOWN     = 180   # frames before crewmate can stun the player again

    def __init__(self, x, y):
        self.pos   = pygame.Vector2(x, y)
        self.size  = 48
        self.speed = self.BASE_SPEED
        self.state = "chase"

        # ── sprite ──────────────────────────────────────────────────
        # TODO: swap path to crewmate asset once it exists
        self.sprite = AnimatedSprite(
            "assets/sprites/crewmate_bw.png",
            num_frames=4,
            frame_duration=8,
            scale=1
        )

        # ── internal timers / state ──────────────────────────────────
        self._stun_cooldown   = 0     # cooldown before crewmate can stun player
        self._stun_timer      = 0     # counts down while crewmate itself is stunned
        self._sabotage_timer  = 0     # countdown to completing a sabotage
        self._sabotage_target = None  # which lever is currently being worked on
        self._sabotage_mode   = False # True after stunning player while levers active

    # ────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ────────────────────────────────────────────────────────────────

    def update(self, player_pos, player_size, levers,
               valid_rooms=None, obstacle_rects=None):
        """
        Call once per frame from the level's game loop.

        player_pos    : pygame.Vector2
        player_size   : int (assumed square)
        levers        : list of objects with .fixed and .rect
        valid_rooms   : list of pygame.Rect, or None for no restriction
        obstacle_rects: list of pygame.Rect for solid objects the crewmate
                        should not walk through
        """

        # ── stunned — do nothing until timer expires ─────────────────
        if self.state == "stunned":
            self.sprite.update(False)
            self._stun_timer -= 1
            if self._stun_timer <= 0:
                self.state = "chase"
            return

        # ── dynamic speed based on currently fixed levers ────────────
        current_fixed = sum(1 for l in levers if l.fixed)
        self.speed = self.BASE_SPEED + current_fixed * self.SPEED_PER_FIX

        # Tick player-stun cooldown
        if self._stun_cooldown > 0:
            self._stun_cooldown -= 1

        # Centre points
        ecx = self.pos.x + self.size // 2
        ecy = self.pos.y + self.size // 2
        pcx = player_pos.x + player_size // 2
        pcy = player_pos.y + player_size // 2

        # ── decide state ─────────────────────────────────────────────
        fixed_levers = [l for l in levers if l.fixed]

        if not fixed_levers:
            # Nothing to sabotage — reset flag and chase
            self._sabotage_mode   = False
            self._sabotage_target = None
            self._sabotage_timer  = 0
            self.state = "chase"
            self._move_to_player(ecx, ecy, pcx, pcy,
                                 valid_rooms, obstacle_rects)
        elif self._sabotage_mode:
            # Was triggered to sabotage after a stun — go undo a lever
            self.state = "sabotage"
            self._move_to_sabotage(ecx, ecy, fixed_levers,
                                   valid_rooms, obstacle_rects)
        else:
            # Levers are active but crewmate hasn't stunned yet — chase first
            self.state = "chase"
            self._move_to_player(ecx, ecy, pcx, pcy,
                                 valid_rooms, obstacle_rects)

        self.sprite.update(moving=True)

    def try_stun_player(self, player_pos, player_size, has_fixed_levers=False):
        """
        Call once per frame after update().
        has_fixed_levers: pass True when at least one lever is currently active.

        Returns True the moment the crewmate touches the player AND the
        cooldown has expired.  The level applies whatever stun it wants.
        When has_fixed_levers is True the crewmate enters sabotage mode
        immediately after the stun so it goes undo a lever next.
        """
        if self.state == "stunned" or self._stun_cooldown > 0:
            return False
        if self.get_rect().colliderect(
                pygame.Rect(player_pos.x, player_pos.y,
                            player_size, player_size)):
            self._stun_cooldown = self.STUN_COOLDOWN
            if has_fixed_levers:
                self._sabotage_mode = True
            return True
        return False

    def stun(self, duration=180):
        """Call this when a thrown wrench hits the crewmate."""
        self.state            = "stunned"
        self._stun_timer      = duration
        self._sabotage_mode   = False  # interrupt sabotage — player earns breathing room
        self._sabotage_target = None
        self._sabotage_timer  = 0

    def draw(self, screen):
        self.sprite.draw(screen, int(self.pos.x), int(self.pos.y))

        try:
            font = pygame.font.SysFont("courier", 12)
        except Exception:
            font = pygame.font.SysFont(None, 12)

        if self.state == "chase":
            label = font.render("!", True, (255, 160, 0))
            screen.blit(label, (self.pos.x + 8, self.pos.y - 18))
        elif self.state == "sabotage":
            # Show sabotage progress bar above sprite
            if self._sabotage_timer > 0:
                pct    = 1.0 - self._sabotage_timer / self.SABOTAGE_DURATION
                bar_w  = int(40 * pct)
                bar_x  = int(self.pos.x + 4)
                bar_y  = int(self.pos.y - 10)
                pygame.draw.rect(screen, (60, 60, 60),
                                 (bar_x, bar_y, 40, 5))
                pygame.draw.rect(screen, (255, 60, 60),
                                 (bar_x, bar_y, bar_w, 5))
            label = font.render("!!", True, (255, 60, 60))
            screen.blit(label, (self.pos.x + 4, self.pos.y - 18))
        elif self.state == "stunned":
            label = font.render("zz", True, (150, 150, 255))
            screen.blit(label, (self.pos.x + 4, self.pos.y - 18))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    # ────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ────────────────────────────────────────────────────────────────

    def _move_to_player(self, ecx, ecy, pcx, pcy,
                        valid_rooms, obstacle_rects):
        direction = pygame.Vector2(pcx - ecx, pcy - ecy)
        if direction.length() == 0:
            return
        self._apply_move(direction.normalize(), valid_rooms, obstacle_rects)

    def _move_to_sabotage(self, ecx, ecy, fixed_levers,
                          valid_rooms, obstacle_rects):
        nearest = min(
            fixed_levers,
            key=lambda l: pygame.Vector2(ecx, ecy).distance_to(
                pygame.Vector2(l.rect.centerx, l.rect.centery))
        )

        target    = pygame.Vector2(nearest.rect.centerx, nearest.rect.centery)
        direction = target - pygame.Vector2(ecx, ecy)

        if direction.length() < self.SABOTAGE_RADIUS:
            # Within range — work on it
            if self._sabotage_target is not nearest:
                # Switched to a new target, reset timer
                self._sabotage_target = nearest
                self._sabotage_timer  = self.SABOTAGE_DURATION
            else:
                self._sabotage_timer -= 1
                if self._sabotage_timer <= 0:
                    nearest.fixed         = False
                    self._sabotage_target = None
                    self._sabotage_timer  = 0
                    self._sabotage_mode   = False  # done — back to chase
        else:
            # Not yet in range — reset timer and keep walking
            if self._sabotage_target is nearest:
                self._sabotage_target = None
                self._sabotage_timer  = 0
            self._apply_move(direction.normalize(), valid_rooms, obstacle_rects)

    def _apply_move(self, direction, valid_rooms, obstacle_rects):
        """Sliding collision — try full move, then X-only, then Y-only."""
        full    = self.pos + direction * self.speed
        axial_x = pygame.Vector2(self.pos.x + direction.x * self.speed,
                                 self.pos.y)
        axial_y = pygame.Vector2(self.pos.x,
                                 self.pos.y + direction.y * self.speed)

        if (self._in_valid_area(full, valid_rooms) and
                not self._hits_obstacle(full, obstacle_rects)):
            self.pos = full
        elif (self._in_valid_area(axial_x, valid_rooms) and
                not self._hits_obstacle(axial_x, obstacle_rects)):
            self.pos = axial_x
        elif (self._in_valid_area(axial_y, valid_rooms) and
                not self._hits_obstacle(axial_y, obstacle_rects)):
            self.pos = axial_y

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect) for room in valid_rooms)

    def _hits_obstacle(self, pos, obstacle_rects):
        if not obstacle_rects:
            return False
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(entity_rect.colliderect(r) for r in obstacle_rects)
