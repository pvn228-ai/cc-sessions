"""World entities: tiles, the Karcite Searing hazard, loot, props, and the
Pinchling enemy.

Drawing lives on each entity; the active Room applies a (currently zero) screen
offset at draw time. Gameplay logic that needs to see the player (enemy AI,
hazard ticks, pickups) is driven from ``Room.update``.
"""

import math

import pygame

from . import settings as cfg


# --------------------------------------------------------------------------- tiles
class Tile(pygame.sprite.Sprite):
    """A solid block. ``theme`` selects the surface vs cave palette."""

    def __init__(self, x, y, theme="surface"):
        super().__init__()
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)
        self.theme = theme

    def draw(self, surface, offset):
        r = self.rect.move(offset)
        if self.theme == "cave":
            pygame.draw.rect(surface, cfg.CAVE_TILE_COLOR, r)
            pygame.draw.rect(surface, cfg.CAVE_TILE_TOP, (r.x, r.y, r.width, 5))
        else:
            pygame.draw.rect(surface, cfg.TILE_COLOR, r)
            pygame.draw.rect(surface, cfg.TILE_TOP_COLOR, (r.x, r.y, r.width, 6))


# ------------------------------------------------------------------- Searing hazard
class Hazard(pygame.sprite.Sprite):
    """A vein/pool of raw Karcite. Glows purple; Sears whoever overlaps it."""

    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)
        self._t = (x + y) * 0.01

    def update(self):
        self._t += 0.08

    def draw(self, surface, offset):
        r = self.rect.move(offset)
        pulse = (math.sin(self._t) + 1) * 0.5  # 0..1
        pygame.draw.rect(surface, cfg.KARCITE_DARK, r)
        glow = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        alpha = int(90 + pulse * 110)
        glow.fill((*cfg.KARCITE_GLOW, alpha))
        surface.blit(glow, r.topleft)
        # crystalline shards
        cx, cy = r.center
        for dx in (-9, 0, 9):
            pygame.draw.polygon(
                surface, cfg.KARCITE_COLOR,
                [(cx + dx, cy - 9), (cx + dx - 4, cy + 8), (cx + dx + 4, cy + 8)],
            )


# --------------------------------------------------------------------------- loot
class Loot(pygame.sprite.Sprite):
    """A pickup that bobs. ``kind`` is 'karcite' or 'coin'."""

    def __init__(self, x, y, kind="karcite", value=1):
        super().__init__()
        self.rect = pygame.Rect(x + 10, y + 10, cfg.TILE_SIZE - 20, cfg.TILE_SIZE - 20)
        self.kind = kind
        self.value = value
        self._t = (x + y) * 0.02

    def update(self):
        self._t += 0.12

    def draw(self, surface, offset):
        bob = math.sin(self._t) * 3
        cx = self.rect.centerx + offset[0]
        cy = self.rect.centery + offset[1] + bob
        if self.kind == "coin":
            pygame.draw.circle(surface, cfg.COIN_COLOR, (int(cx), int(cy)), 7)
            pygame.draw.circle(surface, (255, 240, 180), (int(cx - 2), int(cy - 2)), 3)
        else:  # karcite shard
            pts = [(cx, cy - 9), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)]
            pygame.draw.polygon(surface, cfg.LOOT_COLOR, pts)
            pygame.draw.polygon(surface, cfg.KARCITE_GLOW, pts, 1)


# -------------------------------------------------------------------------- props
class Prop(pygame.sprite.Sprite):
    """An interactable, non-colliding fixture (NPC, entrance, stairs)."""

    def __init__(self, x, y, kind, w=cfg.TILE_SIZE, h=cfg.TILE_SIZE, line=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind            # "npc" | "entrance" | "stairs"
        self.line = line            # dialogue for npc

    @property
    def prompt(self):
        return {"npc": "talk", "entrance": "descend", "stairs": "go down",
                "exit": "climb out"}.get(self.kind, "use")

    def draw(self, surface, offset):
        r = self.rect.move(offset)
        if self.kind == "npc":
            body = pygame.Rect(r.centerx - 9, r.bottom - 26, 18, 26)
            pygame.draw.rect(surface, cfg.NPC_COLOR, body, border_radius=6)
            pygame.draw.circle(surface, cfg.NPC_COLOR, (r.centerx, r.bottom - 30), 8)
        elif self.kind == "entrance":
            pygame.draw.ellipse(surface, cfg.ENTRANCE_COLOR,
                                (r.x, r.y + r.height // 3, r.width, r.height * 2 // 3))
            pygame.draw.rect(surface, (60, 50, 70),
                             (r.x - 4, r.bottom - 6, r.width + 8, 6))
        elif self.kind == "stairs":
            step = r.height // 4
            for i in range(4):
                pygame.draw.rect(surface, cfg.STAIRS_COLOR,
                                 (r.x + i * (r.width // 5), r.bottom - (i + 1) * step,
                                  r.width - i * (r.width // 5), step))
        elif self.kind == "exit":
            # Stairs the other way — climbing back toward the light.
            step = r.height // 4
            for i in range(4):
                pygame.draw.rect(surface, cfg.STAIRS_COLOR,
                                 (r.right - (r.width - i * (r.width // 5)),
                                  r.bottom - (i + 1) * step,
                                  r.width - i * (r.width // 5), step))
            pygame.draw.rect(surface, (120, 160, 200), (r.x, r.y, r.width, 4))


# ----------------------------------------------------------------------- Pinchling
class Pinchling(pygame.sprite.Sprite):
    """A guarding crab. Faces the player, claws up. Front swings bounce off the
    guard; you must FLANK it, PUNISH its claw wind-up, PLUNGE from above, or crack
    its shell with a Shellbreaker (heavy) to open a stagger window."""

    def __init__(self, x, y, theme="surface"):
        super().__init__()
        self.rect = pygame.Rect(x + 4, y + 12, cfg.TILE_SIZE - 8, cfg.TILE_SIZE - 12)
        self.theme = theme
        self.hp = cfg.PINCHLING_HP
        self.facing = -1
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.dead = False

        self._patrol_dir = 1
        self._stagger = 0
        self._windup = 0
        self._lunge = 0
        self._cooldown = 0
        self._flash = 0

    # ------ state helpers
    def staggered(self):
        return self._stagger > 0

    def open(self):
        """Guard is down (punishable): mid wind-up or staggered."""
        return self._windup > 0 or self._stagger > 0

    # ------ taking a hit from the player
    def receive(self, damage, attack_type, attacker_centerx):
        """Decide whether a player attack lands, per the shell rules. Returns
        True if damage was applied (so the swing consumes its hit)."""
        attacker_side = 1 if attacker_centerx >= self.rect.centerx else -1
        from_front = attacker_side == self.facing

        if attack_type == "plunge":
            applied = True                      # from above, ignores guard
        elif attack_type == "heavy":
            applied = True                      # Shellbreaker always lands...
            if from_front and not self.open():
                self._stagger = cfg.PINCHLING_STAGGER_FRAMES   # ...and cracks the shell
                self._windup = self._lunge = 0
        elif not from_front:
            applied = True                      # flank to the soft joints
        elif self.open():
            applied = True                      # punish the raised claw / stagger
        else:
            applied = False                     # bounced off the frontal guard

        if applied:
            self.hp -= damage
            self._flash = 6
            self.rect.x += -attacker_side * 7   # knock away from the blow
            if self.hp <= 0:
                self.dead = True
                self.kill()
        return applied

    def touches(self, player):
        """Contact damage — except while staggered (you've earned the opening)."""
        return not self.staggered() and self.rect.colliderect(player.rect)

    # ------ AI + physics
    def update(self, tiles, player):
        if self.dead:
            return
        if self._flash > 0:
            self._flash -= 1
        if self._cooldown > 0:
            self._cooldown -= 1

        if self.staggered():
            self._stagger -= 1
            self.vel.x = 0
        else:
            self._face_and_act(player)

        # gravity + collision
        self.vel.y = min(self.vel.y + cfg.GRAVITY, cfg.MAX_FALL_SPEED)
        self.rect.x += round(self.vel.x)
        self._resolve(tiles, "x")
        self.on_ground = False
        self.rect.y += round(self.vel.y)
        self._resolve(tiles, "y")

    def _face_and_act(self, player):
        dx = player.rect.centerx - self.rect.centerx
        aggro = abs(dx) < cfg.SCREEN_WIDTH * 0.45 and abs(player.rect.centery - self.rect.centery) < 120

        if self._lunge > 0:
            self._lunge -= 1
            self.vel.x = self.facing * cfg.PINCHLING_LUNGE_SPEED
            return
        if self._windup > 0:
            self._windup -= 1
            self.vel.x = 0
            if self._windup == 0:
                self._lunge = cfg.PINCHLING_LUNGE_FRAMES   # claw drops -> lunge
                self._cooldown = cfg.PINCHLING_ATTACK_COOLDOWN
            return

        if aggro:
            self.facing = 1 if dx > 0 else -1
            if abs(dx) < cfg.TILE_SIZE * 2 and self._cooldown <= 0 and self.on_ground:
                self._windup = cfg.PINCHLING_WINDUP_FRAMES   # telegraph: raise claw
                self.vel.x = 0
            else:
                self.vel.x = self.facing * cfg.PINCHLING_SPEED
        else:
            self._patrol(player)

    def _patrol(self, _player):
        self.facing = self._patrol_dir
        self.vel.x = self._patrol_dir * cfg.PINCHLING_SPEED

    def _resolve(self, tiles, axis):
        for tile in tiles:
            if not self.rect.colliderect(tile.rect):
                continue
            if axis == "x":
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                self.vel.x = 0
                self._patrol_dir *= -1
            else:
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                self.vel.y = 0

    # ------ drawing
    def draw(self, surface, offset):
        r = self.rect.move(offset)
        if self._flash > 0:
            color = (255, 255, 255)
        elif self.staggered():
            color = cfg.PINCHLING_STAGGER_COLOR
        else:
            color = cfg.PINCHLING_COLOR
        pygame.draw.ellipse(surface, color, r)
        # shell ridge
        pygame.draw.arc(surface, cfg.PINCHLING_SHELL_COLOR,
                        (r.x, r.y - 4, r.width, r.height), 3.3, 6.1, 3)
        # eyes (on stalks, toward facing)
        ex = r.centerx + self.facing * 6
        ey = r.y + 4
        for s in (-5, 5):
            pygame.draw.line(surface, cfg.PINCHLING_SHELL_COLOR, (r.centerx + s, r.y + 6),
                             (ex + s, ey - 4), 2)
            pygame.draw.circle(surface, (250, 250, 250), (ex + s, ey - 5), 3)
            pygame.draw.circle(surface, (20, 20, 20), (ex + s, ey - 5), 1)
        # a claw, raised when winding up (guard down = your moment)
        claw_y = r.y - 6 if self._windup > 0 else r.centery
        cx = r.right + 4 if self.facing > 0 else r.left - 4
        pygame.draw.circle(surface, cfg.PINCHLING_SHELL_COLOR, (cx, claw_y), 7)
        if not self.open():
            # guard shimmer in front
            gx = r.right + 2 if self.facing > 0 else r.left - 2
            pygame.draw.line(surface, (220, 200, 210), (gx, r.y), (gx, r.bottom), 1)
