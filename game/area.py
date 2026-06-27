"""A single screen-sized area of the world.

An Area owns its tiles, coins, and enemies, and runs collision/coin/enemy
logic. Areas are created once and cached by the World, so any coins you
collect stay collected when you leave and come back -- that is what makes
the world feel persistent.

Borders are detected but NOT resolved here: ``check_border`` reports which
edge (if any) the player has crossed, and the World decides whether to
transition to a neighbour or treat the edge as a solid wall.
"""

import pygame

from . import settings as cfg
from .entities import Tile, Coin, Enemy

# Border identifiers returned by ``check_border``.
WEST, EAST, NORTH, SOUTH = "west", "east", "north", "south"


class Area:
    def __init__(self, name, rows):
        self.name = name
        self.tiles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn_tile = None  # (x, y) of a 'P' glyph, if present

        for r in range(cfg.AREA_ROWS):
            row = rows[r] if r < len(rows) else ""
            for c in range(cfg.AREA_COLS):
                char = row[c] if c < len(row) else " "
                x, y = c * cfg.TILE_SIZE, r * cfg.TILE_SIZE
                if char == "#":
                    self.tiles.add(Tile(x, y))
                elif char == "C":
                    self.coins.add(Coin(x, y))
                elif char == "E":
                    self.enemies.add(Enemy(x, y))
                elif char == "P":
                    self.spawn_tile = (x, y)

    # -- per-frame logic -----------------------------------------------------
    def update(self, player):
        """Advance this area for one frame. Returns coins collected this frame."""
        tiles = self.tiles.sprites()
        player.update(tiles)
        for enemy in self.enemies:
            enemy.update(tiles)
        self.coins.update()

        gained = pygame.sprite.spritecollide(player, self.coins, dokill=True)
        return len(gained)

    def player_hit_enemy(self, player):
        return any(player.rect.colliderect(e.rect) for e in self.enemies)

    # -- borders -------------------------------------------------------------
    def check_border(self, player):
        """Which edge the player has crossed this frame, or None."""
        if player.rect.left < 0:
            return WEST
        if player.rect.right > cfg.SCREEN_WIDTH:
            return EAST
        if player.rect.top < 0:
            return NORTH
        if player.rect.top > cfg.SCREEN_HEIGHT:  # fell through the bottom
            return SOUTH
        return None

    def clamp_player(self, player, border):
        """Keep the player inside this area (used when a border has no neighbour)."""
        if border == WEST:
            player.rect.left = 0
            player.vel.x = 0
        elif border == EAST:
            player.rect.right = cfg.SCREEN_WIDTH
            player.vel.x = 0
        elif border == NORTH:
            player.rect.top = 0
            player.vel.y = 0
        elif border == SOUTH:
            # No floor below: bounce them back up so they don't vanish.
            player.rect.bottom = cfg.SCREEN_HEIGHT
            player.vel.y = 0

    # -- drawing -------------------------------------------------------------
    def draw(self, surface, offset=(0, 0)):
        for tile in self.tiles:
            tile.draw(surface, offset)
        for coin in self.coins:
            coin.draw(surface, offset)
        for enemy in self.enemies:
            enemy.draw(surface, offset)
