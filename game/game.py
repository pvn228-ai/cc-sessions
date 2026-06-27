"""Top-level application: window, main loop, scenes, HUD, and the run loop.

Scenes: TITLE -> SURFACE (Larkhollow) <-> DUNGEON (the delve) ; DEATH overlay.
The Game owns the shared player and the loot. Loot picked up underground is the
"run loot"; you BANK it by climbing out or reaching the bottom, and you LOSE it
if you die. The town is safe — returning there heals you.
"""

import pygame

from . import settings as cfg
from .player import Player
from .world import World
from .dungeon import Dungeon

TITLE, SURFACE, DUNGEON, DEATH = "title", "surface", "dungeon", "death"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("consolas,menlo,monospace", 20)
        self.big = pygame.font.SysFont("consolas,menlo,monospace", 52, bold=True)
        self.small = pygame.font.SysFont("consolas,menlo,monospace", 16)

        self._sky = self._gradient(cfg.SKY_TOP, cfg.SKY_BOTTOM)
        self._cave = self._gradient(cfg.CAVE_TOP, cfg.CAVE_BOTTOM)

        self.player = Player(0, 0)
        self.world = None
        self.dungeon = None
        self.state = TITLE
        self.run_loot = {"karcite": 0, "coin": 0}
        self.banked = {"karcite": 0, "coin": 0}
        self.dialogue = None
        self.flash = None       # transient (text, frames) banner

    # ---------------------------------------------------------------- setup
    def _gradient(self, top, bottom):
        surf = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        for y in range(cfg.SCREEN_HEIGHT):
            t = y / cfg.SCREEN_HEIGHT
            surf.fill(
                [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)],
                (0, y, cfg.SCREEN_WIDTH, 1),
            )
        return surf

    def _new_game(self):
        self.player = Player(0, 0)
        self.world = World(self.player)
        self.run_loot = {"karcite": 0, "coin": 0}
        self.banked = {"karcite": 0, "coin": 0}
        self.state = SURFACE

    @property
    def scene(self):
        return self.dungeon if self.state == DUNGEON else self.world

    # ----------------------------------------------------------- main loop
    def run(self):
        while self.running:
            self._events()
            self._update()
            self._draw()
            self.clock.tick(cfg.FPS)
        pygame.quit()

    def _events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                self._keydown(e.key)

    def _keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
            return
        if self.dialogue is not None:
            self.dialogue = None
            return
        if self.state == TITLE:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._new_game()
            return
        if self.state == DEATH:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._respawn_in_town()
            return
        # In-play controls (SURFACE / DUNGEON).
        if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.on_jump()
        elif key in (pygame.K_j, pygame.K_x):
            down = pygame.key.get_pressed()
            if not self.player.on_ground and (down[pygame.K_DOWN] or down[pygame.K_s]):
                self.player.on_plunge()
            else:
                self.player.on_attack_light()
        elif key in (pygame.K_k, pygame.K_c):
            self.player.on_attack_heavy()
        elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.player.on_dash()
        elif key == pygame.K_e:
            self._interact()

    def _interact(self):
        ev = self.scene.interact()
        if ev is None:
            return
        tag = ev[0]
        if tag == "dialogue":
            self.dialogue = ev[1]
        elif tag == "enter_dungeon":
            self.dungeon = Dungeon(self.player, max_depth=2)
            self.state = DUNGEON
            self.flash = ("You descend into the Drownways...", 90)
        elif tag == "exit":
            self._return_to_town("You climb back into the light.")
        elif tag == "bottom":
            self._return_to_town("You reach the bottom and escape — for now.")
        elif tag == "descend":
            self.flash = (f"Depth {self.dungeon.depth}", 70)

    # ----------------------------------------------------------- updates
    def _update(self):
        if self.flash is not None:
            self.flash = (self.flash[0], self.flash[1] - 1)
            if self.flash[1] <= 0:
                self.flash = None
        if self.state in (SURFACE, DUNGEON) and self.dialogue is None:
            self.player.handle_input(pygame.key.get_pressed())
            result = self.scene.update()
            for lt in result.get("picked", []):
                self.run_loot[lt.kind] = self.run_loot.get(lt.kind, 0) + lt.value
            if self.player.dead:
                self.state = DEATH

    def _return_to_town(self, message):
        for k, v in self.run_loot.items():
            self.banked[k] = self.banked.get(k, 0) + v
        self.run_loot = {"karcite": 0, "coin": 0}
        self.dungeon = None
        self.world.return_to_entrance()
        self.player.revive()
        self.state = SURFACE
        self.flash = (message, 120)

    def _respawn_in_town(self):
        self.run_loot = {"karcite": 0, "coin": 0}   # loot lost on death
        self.dungeon = None
        self.world.return_to_entrance()
        self.player.revive()
        self.state = SURFACE
        self.flash = ("You wake in Larkhollow. Your haul is lost.", 120)

    # ----------------------------------------------------------- drawing
    def _draw(self):
        self.screen.blit(self._cave if self.state == DUNGEON else self._sky, (0, 0))
        if self.state == TITLE:
            self._draw_title()
        elif self.state in (SURFACE, DUNGEON):
            self.scene.draw(self.screen)
            self._draw_hud()
            if self.dialogue is not None:
                self._draw_dialogue()
        elif self.state == DEATH:
            if self.world:
                self.world.draw(self.screen)
            self._draw_death()
        self._draw_flash()
        pygame.display.flip()

    def _text(self, text, font, color, center):
        sh = font.render(text, True, cfg.SHADOW_COLOR)
        la = font.render(text, True, color)
        rect = la.get_rect(center=center)
        self.screen.blit(sh, rect.move(2, 2))
        self.screen.blit(la, rect)

    def _draw_hud(self):
        # Hearts.
        for i in range(cfg.PLAYER_MAX_HP):
            col = cfg.HP_COLOR if i < self.player.hp else cfg.HP_EMPTY
            pygame.draw.rect(self.screen, col, (16 + i * 22, 16, 18, 18), border_radius=4)
        # Stamina bar.
        pygame.draw.rect(self.screen, cfg.HP_EMPTY, (16, 40, 140, 10), border_radius=4)
        w = int(140 * self.player.stamina / cfg.STAMINA_MAX)
        pygame.draw.rect(self.screen, cfg.STAMINA_COLOR, (16, 40, w, 10), border_radius=4)
        # Loot + location.
        loot = f"Karcite {self.run_loot['karcite']}   Coin {self.run_loot['coin']}"
        self.screen.blit(self.font.render(loot, True, cfg.LOOT_COLOR), (16, 58))
        name = self.scene.name
        label = self.font.render(name, True, cfg.TEXT_COLOR)
        self.screen.blit(label, (cfg.SCREEN_WIDTH - label.get_width() - 16, 16))
        if self.state == DUNGEON:
            banked = self.small.render(
                f"banked: K{self.banked['karcite']} C{self.banked['coin']}",
                True, cfg.DIM_TEXT)
            self.screen.blit(banked, (cfg.SCREEN_WIDTH - banked.get_width() - 16, 40))

        # Interaction + controls.
        prompt = self.scene.interact_prompt()
        if prompt:
            self._text(f"[E] {prompt}", self.font, cfg.TEXT_COLOR,
                       (self.player.rect.centerx, self.player.rect.top - 18))
        controls = "Move A/D · Jump W · Swing J · Shellbreaker K · Dash Shift · Down+J plunge · E interact"
        c = self.small.render(controls, True, cfg.DIM_TEXT)
        self.screen.blit(c, (16, cfg.SCREEN_HEIGHT - 24))

    def _draw_dialogue(self):
        box = pygame.Rect(60, cfg.SCREEN_HEIGHT - 150, cfg.SCREEN_WIDTH - 120, 96)
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        panel.fill((16, 20, 28, 230))
        self.screen.blit(panel, box.topleft)
        pygame.draw.rect(self.screen, cfg.NPC_COLOR, box, 2, border_radius=6)
        self._wrap(self.dialogue, box.inflate(-28, -28), self.font, cfg.TEXT_COLOR)
        self.screen.blit(self.small.render("[any key]", True, cfg.DIM_TEXT),
                         (box.right - 90, box.bottom - 22))

    def _wrap(self, text, rect, font, color):
        words, line, y = text.split(" "), "", rect.y
        for word in words:
            test = (line + " " + word).strip()
            if font.size(test)[0] > rect.width and line:
                self.screen.blit(font.render(line, True, color), (rect.x, y))
                y += font.get_height() + 2
                line = word
            else:
                line = test
        if line:
            self.screen.blit(font.render(line, True, color), (rect.x, y))

    def _draw_flash(self):
        if self.flash is None:
            return
        text, frames = self.flash
        alpha = min(255, frames * 6)
        label = self.font.render(text, True, cfg.TEXT_COLOR)
        label.set_alpha(alpha)
        self.screen.blit(label, label.get_rect(center=(cfg.SCREEN_WIDTH // 2, 90)))

    def _draw_title(self):
        cx = cfg.SCREEN_WIDTH // 2
        self._text("LARKHOLLOW", self.big, cfg.LOOT_COLOR, (cx, 180))
        for i, line in enumerate([
            "A Delver's Tale  ·  v1 vertical slice",
            "",
            "Raid the Drownways. Crack the crabs. Climb out with your haul.",
            "Die, and you lose what you carried.",
            "",
            "Press ENTER to begin   ·   ESC to quit",
        ]):
            self._text(line, self.font, cfg.TEXT_COLOR, (cx, 250 + i * 30))

    def _draw_death(self):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 10, 16, 180))
        self.screen.blit(overlay, (0, 0))
        cx = cfg.SCREEN_WIDTH // 2
        self._text("You fall.", self.big, cfg.HP_COLOR, (cx, 240))
        self._text("Your haul is lost to the deep.", self.font, cfg.TEXT_COLOR, (cx, 310))
        self._text("Press ENTER to wake in Larkhollow", self.font, cfg.DIM_TEXT, (cx, 350))
