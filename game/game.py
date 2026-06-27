"""Top-level game application: window, main loop, and state machine.

States: MENU -> EXPLORING. There is no "win" -- the world is an open map of
connected areas you roam freely. Cross a border to travel between areas;
the world remembers what you have collected.
"""

import pygame

from . import settings as cfg
from . import world_data
from .world import World

MENU = "menu"
EXPLORING = "exploring"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("consolas,menlo,monospace", 22)
        self.big_font = pygame.font.SysFont("consolas,menlo,monospace", 56, bold=True)

        self._bg = self._make_background()
        self._map_bounds = self._compute_map_bounds()

        self.state = MENU
        self.world = None

    # -- setup helpers -------------------------------------------------------
    def _make_background(self):
        """Pre-render a vertical sky gradient once."""
        bg = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        for y in range(cfg.SCREEN_HEIGHT):
            t = y / cfg.SCREEN_HEIGHT
            color = [
                int(cfg.SKY_TOP[i] + (cfg.SKY_BOTTOM[i] - cfg.SKY_TOP[i]) * t)
                for i in range(3)
            ]
            pygame.draw.line(bg, color, (0, y), (cfg.SCREEN_WIDTH, y))
        return bg

    def _compute_map_bounds(self):
        cols = [c for (c, _) in world_data.WORLD]
        rows = [r for (_, r) in world_data.WORLD]
        return min(cols), min(rows), max(cols), max(rows)

    def _start_game(self):
        self.world = World()
        self.state = EXPLORING

    # -- main loop -----------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(cfg.FPS)
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.state == EXPLORING:
                    self.world.restart_area()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.state == MENU:
                    self._start_game()

    def _update(self):
        if self.state == EXPLORING:
            self.world.handle_input(pygame.key.get_pressed())
            self.world.update()

    # -- rendering -----------------------------------------------------------
    def _draw(self):
        self.screen.blit(self._bg, (0, 0))
        if self.state == MENU:
            self._draw_menu()
        elif self.state == EXPLORING:
            self.world.draw(self.screen)
            self._draw_hud()
            self._draw_minimap()
        pygame.display.flip()

    def _text(self, text, font, color, center):
        shadow = font.render(text, True, cfg.SHADOW_COLOR)
        label = font.render(text, True, color)
        rect = label.get_rect(center=center)
        self.screen.blit(shadow, rect.move(2, 2))
        self.screen.blit(label, rect)

    def _draw_hud(self):
        w = self.world
        self.screen.blit(
            self.font.render(f"{w.area.name}  {w.coord}", True, cfg.TEXT_COLOR), (16, 14)
        )
        self.screen.blit(
            self.font.render(
                f"Coins: {w.coins_collected}   Deaths: {w.deaths}", True, cfg.TEXT_COLOR
            ),
            (16, 42),
        )
        hint = "Arrows/WASD move - Space jump - cross a border to travel - R reset area"
        self.screen.blit(self.font.render(hint, True, cfg.TEXT_COLOR), (16, cfg.SCREEN_HEIGHT - 32))

    def _draw_minimap(self):
        """A small grid in the top-right showing visited areas and your spot."""
        min_c, min_r, max_c, max_r = self._map_bounds
        cell, pad = 18, 3
        grid_w = (max_c - min_c + 1) * (cell + pad) + pad
        grid_h = (max_r - min_r + 1) * (cell + pad) + pad
        ox = cfg.SCREEN_WIDTH - grid_w - 16
        oy = 16

        panel = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
        panel.fill((20, 24, 32, 150))
        self.screen.blit(panel, (ox, oy))

        for (c, r) in world_data.WORLD:
            x = ox + pad + (c - min_c) * (cell + pad)
            y = oy + pad + (r - min_r) * (cell + pad)
            here = (c, r) == self.world.coord
            visited = (c, r) in self.world._cache
            color = cfg.GOAL_COLOR if here else (cfg.TILE_TOP_COLOR if visited else (90, 100, 120))
            pygame.draw.rect(self.screen, color, (x, y, cell, cell), border_radius=3)

    def _draw_menu(self):
        cx = cfg.SCREEN_WIDTH // 2
        self._text(cfg.TITLE, self.big_font, cfg.PLAYER_COLOR, (cx, 190))
        lines = [
            "Explore a persistent world of connected areas.",
            "Walk off an edge to travel to the next area.",
            "",
            "Press ENTER to begin    -    ESC to quit",
        ]
        for i, line in enumerate(lines):
            self._text(line, self.font, cfg.TEXT_COLOR, (cx, 290 + i * 34))
