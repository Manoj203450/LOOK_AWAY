"""
sprite_loader.py  —  Look Away
Drop this file in your project root, or copy the class/function you need.

Sprite sheets:
  player.png       — 4 frames × 48px  (walk cycle)
  enemy.png        — 4 frames × 48px  (shamble cycle)
  weeping_angel.png— 2 frames × 48px  (F0=still, F1=moving/glowing)

Put the PNGs in  assets/sprites/
"""

import pygame

FRAME_SIZE = 48   # each frame is 48×48 px


class AnimatedSprite:
    """Top-down animated sprite from a horizontal strip sheet."""

    def __init__(self, sheet_path: str, num_frames: int,
                 frame_duration: int = 8, scale: int = 1):
        """
        sheet_path    — path to the sprite sheet PNG
        num_frames    — number of animation frames in the strip
        frame_duration— ticks per frame (lower = faster)
        scale         — integer scale factor (e.g. 1 = 48px, 2 = 96px)
        """
        sheet = pygame.image.load(sheet_path).convert_alpha()
        self.num_frames     = num_frames
        self.frame_duration = frame_duration
        self.tick           = 0
        self.current_frame  = 0
        self.size           = FRAME_SIZE * scale

        # Slice + scale each frame
        self.frames = []
        for i in range(num_frames):
            rect  = pygame.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
            frame = sheet.subsurface(rect)
            if scale != 1:
                frame = pygame.transform.scale(
                    frame, (self.size, self.size))
            self.frames.append(frame)

    def update(self, moving: bool = True):
        """Call once per game tick. Pass moving=False to freeze animation."""
        if moving:
            self.tick += 1
            if self.tick >= self.frame_duration:
                self.tick = 0
                self.current_frame = (
                    self.current_frame + 1) % self.num_frames

    def get_frame(self) -> pygame.Surface:
        return self.frames[self.current_frame]

    def draw(self, screen: pygame.Surface, x: int, y: int,
             angle_deg: float = 0.0):
        """
        Draw at (x, y). Optionally rotate by angle_deg (top-down facing).
        The sprite's centre is used as the pivot.
        """
        frame = self.get_frame()
        if angle_deg:
            frame = pygame.transform.rotate(frame, -angle_deg)
        # Centre the sprite on (x, y) offset
        rect = frame.get_rect()
        screen.blit(frame, (x - rect.width // 2 + self.size // 2,
                             y - rect.height // 2 + self.size // 2))


class WeepingAngelSprite:
    """
    Special-case sprite for the Weeping Angel.
    Frame 0 = frozen/still
    Frame 1 = moving (red-eye glow indicator)
    """

    def __init__(self, sheet_path: str, scale: int = 1):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        self.size   = FRAME_SIZE * scale
        self.frames = []
        for i in range(2):
            rect  = pygame.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
            frame = sheet.subsurface(rect)
            if scale != 1:
                frame = pygame.transform.scale(
                    frame, (self.size, self.size))
            self.frames.append(frame)

    def draw(self, screen: pygame.Surface, x: int, y: int,
             frozen: bool = True):
        """frozen=True → still frame, frozen=False → glowing-eye frame."""
        frame = self.frames[0 if frozen else 1]
        screen.blit(frame, (x, y))


# ─────────────────────────────────────────────────────────────────
# USAGE EXAMPLE  (paste into your level file, adjust paths)
# ─────────────────────────────────────────────────────────────────
#
#   from sprite_loader import AnimatedSprite, WeepingAngelSprite
#
#   # In your setup / __init__:
#   player_spr = AnimatedSprite("assets/sprites/player.png",
#                               num_frames=4, frame_duration=8, scale=1)
#   enemy_spr  = AnimatedSprite("assets/sprites/enemy.png",
#                               num_frames=4, frame_duration=10, scale=1)
#   angel_spr  = WeepingAngelSprite("assets/sprites/weeping_angel.png",
#                                   scale=1)
#
#   # In your game loop (update):
#   player_spr.update(moving=(dx != 0 or dy != 0))
#   enemy_spr.update(moving=(enemy.state != "stunned"))
#
#   # Replace pygame.draw.rect(...) draws with:
#   player_spr.draw(screen, int(player_pos.x), int(player_pos.y))
#   enemy_spr.draw(screen, int(enemy.pos.x), int(enemy.pos.y))
#   angel_spr.draw(screen, int(angel.pos.x), int(angel.pos.y),
#                  frozen=angel.frozen)
#
