"""A single screen-sized Room — the shared unit for both the authored Surface
and the generated dungeon.

A Room parses an ASCII grid into tiles/hazards/loot/props/enemies, draws them,
and resolves per-frame combat (player attacks, enemy contact, Searing, pickups)
in one place so both the Surface (``world``) and the Dungeon reuse it. Border
crossings are detected here but resolved by the caller, which knows the map.

Glyph legend:
    #  solid tile        ^  Karcite hazard (Searing)   *  karcite loot
    $  coin              E  Pinchling enemy            K  Clawknight (plated)
    P  player spawn      N  NPC                        S  smith (the Forge)
    D  dungeon entrance  >  stairs down                <  climb out
    (space) empty
"""

import pygame

from . import settings as cfg
from .entities import Tile, Hazard, Loot, Prop, Pinchling, Clawknight

WEST, EAST, NORTH, SOUTH = "west", "east", "north", "south"


class Room:
    def __init__(self, rows, theme="surface", npc_lines=None):
        self.theme = theme
        self.tiles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.loot = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.props = pygame.sprite.Group()
        self.spawn_tile = None
        self.entrance = None
        self.smith = None
        self.stairs = None
        self.exit_prop = None

        npc_lines = npc_lines or []
        npc_i = 0

        for r in range(cfg.AREA_ROWS):
            row = rows[r] if r < len(rows) else ""
            for c in range(cfg.AREA_COLS):
                ch = row[c] if c < len(row) else " "
                x, y = c * cfg.TILE_SIZE, r * cfg.TILE_SIZE
                if ch == "#":
                    self.tiles.add(Tile(x, y, theme))
                elif ch == "^":
                    self.hazards.add(Hazard(x, y))
                elif ch == "*":
                    self.loot.add(Loot(x, y, "karcite", 1))
                elif ch == "$":
                    self.loot.add(Loot(x, y, "coin", 1))
                elif ch == "E":
                    self.enemies.add(Pinchling(x, y, theme))
                elif ch == "K":
                    self.enemies.add(Clawknight(x, y, theme))
                elif ch == "P":
                    self.spawn_tile = (x, y)
                elif ch == "N":
                    line = npc_lines[npc_i] if npc_i < len(npc_lines) else "..."
                    npc_i += 1
                    self.props.add(Prop(x, y, "npc", line=line))
                elif ch == "S":
                    self.smith = Prop(x, y, "smith")
                    self.props.add(self.smith)
                elif ch == "D":
                    self.entrance = Prop(x, y - cfg.TILE_SIZE, "entrance",
                                         h=cfg.TILE_SIZE * 2)
                    self.props.add(self.entrance)
                elif ch == ">":
                    self.stairs = Prop(x, y, "stairs")
                    self.props.add(self.stairs)
                elif ch == "<":
                    self.exit_prop = Prop(x, y, "exit")
                    self.props.add(self.exit_prop)

    # ----------------------------------------------------------------- update
    def update(self, player):
        """Advance the room one frame. Returns a dict of events for the scene:
        ``{"picked": [Loot,...], "xp": int}``. Death is read from ``player.dead``."""
        tiles = self.tiles.sprites()
        player.update(tiles)
        for enemy in self.enemies:
            enemy.update(tiles, player)
        self.hazards.update()
        self.loot.update()

        xp = self._resolve_attacks(player)
        self._resolve_contact(player)
        self._resolve_searing(player)
        picked = self._resolve_pickups(player)
        return {"picked": picked, "xp": xp}

    def _resolve_attacks(self, player):
        """Apply the live attack hitbox. Returns XP earned from anything felled."""
        if player.attack_rect is None or player.attack_type is None:
            return 0
        xp = 0
        for enemy in list(self.enemies):
            if player.already_hit(enemy):
                continue
            if player.attack_rect.colliderect(enemy.rect):
                enemy.receive(player.attack_damage, player.attack_type, player.rect.centerx)
                player.mark_hit(enemy)
                if enemy.dead:
                    xp += enemy.xp_value
                    self._drop_loot(enemy)
        return xp

    def _drop_loot(self, enemy):
        """A felled Karcon sheds what the element left in it."""
        for i, (kind, value) in enumerate(enemy.drops):
            self.loot.add(Loot(enemy.rect.centerx - cfg.TILE_SIZE // 2 + i * 14,
                               enemy.rect.centery - cfg.TILE_SIZE // 2, kind, value))

    def _resolve_contact(self, player):
        for enemy in self.enemies:
            if enemy.touches(player):
                player.take_hit(enemy.touch_damage, enemy.rect.centerx)

    def _resolve_searing(self, player):
        for hz in self.hazards:
            if player.rect.colliderect(hz.rect):
                player.sear()   # i-frames inside sear() rate-limit the damage
                break

    def _resolve_pickups(self, player):
        hit = pygame.sprite.spritecollide(player, self.loot, dokill=True)
        return hit

    # ----------------------------------------------------------- interaction
    def nearby_prop(self, player):
        """The closest interactable prop within reach, or None."""
        best, best_d = None, 999999
        for prop in self.props:
            if prop.kind not in ("npc", "smith", "entrance", "stairs", "exit"):
                continue
            d = abs(prop.rect.centerx - player.rect.centerx)
            if d < cfg.TILE_SIZE and abs(prop.rect.centery - player.rect.centery) < cfg.TILE_SIZE * 2:
                if d < best_d:
                    best, best_d = prop, d
        return best

    # ---------------------------------------------------------------- borders
    def check_border(self, player):
        if player.rect.left < 0:
            return WEST
        if player.rect.right > cfg.SCREEN_WIDTH:
            return EAST
        if player.rect.top < 0:
            return NORTH
        if player.rect.top > cfg.SCREEN_HEIGHT:
            return SOUTH
        return None

    def clamp_player(self, player, border):
        if border == WEST:
            player.rect.left = 0
        elif border == EAST:
            player.rect.right = cfg.SCREEN_WIDTH
        elif border == NORTH:
            player.rect.top = 0
            player.vel.y = 0
        elif border == SOUTH:
            player.rect.bottom = cfg.SCREEN_HEIGHT
            player.vel.y = 0

    # ---------------------------------------------------------------- drawing
    def draw(self, surface, offset=(0, 0)):
        for hz in self.hazards:
            hz.draw(surface, offset)
        for tile in self.tiles:
            tile.draw(surface, offset)
        for prop in self.props:
            prop.draw(surface, offset)
        for lt in self.loot:
            lt.draw(surface, offset)
        for enemy in self.enemies:
            enemy.draw(surface, offset)
