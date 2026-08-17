"""Top-level application: window, main loop, scenes, HUD, and the run loop.

Scenes: TITLE -> SURFACE (Larkhollow) <-> DUNGEON (the delve) ; DEATH overlay;
FORGE (the shop) opens over the town.

The Game owns the shared player, the run loot, and ``Progress`` — the bank, XP,
and gear that survive between runs. Loot picked up underground is the "run loot";
you BANK it by climbing out or reaching the bottom, and you LOSE it if you die.
XP and gear are never lost. The town is safe — returning there heals you, and the
Sunbound Forge is where the bank becomes power.
"""

import pygame

from . import settings as cfg
from . import progress as prog
from .player import Player
from .world import World
from .dungeon import Dungeon

TITLE, SURFACE, DUNGEON, DEATH, FORGE = "title", "surface", "dungeon", "death", "forge"


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

        self.progress = prog.Progress.load()
        self.player = Player(0, 0, self.progress)
        self.world = None
        self.dungeon = None
        self.state = TITLE
        self.run_loot = {"karcite": 0, "coin": 0}
        self.dialogue = None
        self.flash = None       # transient (text, frames) banner
        self.forge_index = 0    # highlighted gear track in the Forge

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
        self.progress = prog.Progress.load()   # pick up where the last delve left off
        self.player = Player(0, 0, self.progress)
        self.world = World(self.player)
        self.run_loot = {"karcite": 0, "coin": 0}
        self.state = SURFACE

    @property
    def banked(self):
        return self.progress.banked

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
        if self.state == FORGE:
            self._forge_key(key)
            return
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
        elif tag == "forge":
            self.state = FORGE
            self.forge_index = 0

    # ------------------------------------------------------------- the forge
    def _forge_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_e, pygame.K_q):
            self.state = SURFACE
            self.progress.save()
            return
        if key in (pygame.K_UP, pygame.K_w):
            self.forge_index = (self.forge_index - 1) % len(prog.GEAR)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.forge_index = (self.forge_index + 1) % len(prog.GEAR)
        elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j):
            self._forge_buy()

    def _forge_buy(self):
        track = prog.GEAR[self.forge_index]
        if self.progress.next_cost(track.key) is None:
            self.flash = (f"{track.name} is already at its finest.", 80)
            return
        hearts = self.player.max_hp
        if not self.progress.buy(track.key):
            self.flash = ("Not enough in the bank for that.", 80)
            return
        tier = self.progress.tier(track.key)
        # Gear that adds a heart hands it to you filled, there and then.
        self.player.hp += self.player.max_hp - hearts
        self.progress.save()
        self.flash = (f"{track.name} {'I' * tier} — {track.describe(tier)}", 120)

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
            self._gain_xp(result.get("xp", 0))
            if self.player.dead:
                self.state = DEATH

    def _gain_xp(self, amount):
        """XP is earned, not carried — a death never takes it back."""
        if not amount:
            return
        levels = self.progress.add_xp(amount)
        if levels:
            # A level is a heart, and the wind back in your lungs.
            self.player.hp = min(self.player.max_hp, self.player.hp + levels)
            self.player.stamina = self.player.stamina_max
            self.flash = (f"Level {self.progress.level} — you steady your grip.", 120)
            self.progress.save()

    def _return_to_town(self, message):
        self.progress.bank(self.run_loot)
        self.progress.save()
        self.run_loot = {"karcite": 0, "coin": 0}
        self.dungeon = None
        self.world.return_to_entrance()
        self.player.revive()
        self.state = SURFACE
        self.flash = (message, 120)

    def _respawn_in_town(self):
        self.run_loot = {"karcite": 0, "coin": 0}   # loot lost on death (XP is not)
        self.progress.save()
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
        elif self.state == FORGE:
            self.world.draw(self.screen)
            self._draw_forge()
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
        # Hearts — levels and the Ward add to the row.
        for i in range(self.player.max_hp):
            col = cfg.HP_COLOR if i < self.player.hp else cfg.HP_EMPTY
            pygame.draw.rect(self.screen, col, (16 + i * 22, 16, 18, 18), border_radius=4)
        # Stamina bar.
        pygame.draw.rect(self.screen, cfg.HP_EMPTY, (16, 40, 140, 10), border_radius=4)
        w = int(140 * self.player.stamina / self.player.stamina_max)
        pygame.draw.rect(self.screen, cfg.STAMINA_COLOR, (16, 40, w, 10), border_radius=4)
        # XP bar toward the next level.
        pygame.draw.rect(self.screen, cfg.HP_EMPTY, (16, 54, 140, 6), border_radius=3)
        xw = int(140 * min(1.0, self.progress.xp / max(1, self.progress.xp_to_next)))
        pygame.draw.rect(self.screen, cfg.XP_COLOR, (16, 54, xw, 6), border_radius=3)
        self.screen.blit(self.small.render(f"Lv {self.progress.level}", True, cfg.XP_COLOR),
                         (162, 48))
        # Loot + location.
        loot = f"Karcite {self.run_loot['karcite']}   Coin {self.run_loot['coin']}"
        self.screen.blit(self.font.render(loot, True, cfg.LOOT_COLOR), (16, 66))
        name = self.scene.name
        label = self.font.render(name, True, cfg.TEXT_COLOR)
        self.screen.blit(label, (cfg.SCREEN_WIDTH - label.get_width() - 16, 16))
        banked = self.small.render(
            f"banked: K{self.banked['karcite']} C{self.banked['coin']}",
            True, cfg.DIM_TEXT)
        self.screen.blit(banked, (cfg.SCREEN_WIDTH - banked.get_width() - 16, 40))
        gear = self.small.render(self._gear_line(), True, cfg.DIM_TEXT)
        self.screen.blit(gear, (cfg.SCREEN_WIDTH - gear.get_width() - 16, 58))

    def _gear_line(self):
        return "  ".join(f"{g.name.split()[-1]} {self.progress.tier(g.key)}"
                         for g in prog.GEAR)

        # Interaction + controls.
        prompt = self.scene.interact_prompt()
        if prompt:
            self._text(f"[E] {prompt}", self.font, cfg.TEXT_COLOR,
                       (self.player.rect.centerx, self.player.rect.top - 18))
        controls = "Move A/D · Jump W · Swing J · Shellbreaker K · Dash Shift · Down+J plunge · E interact"
        c = self.small.render(controls, True, cfg.DIM_TEXT)
        self.screen.blit(c, (16, cfg.SCREEN_HEIGHT - 24))

    def _draw_forge(self):
        """The Sunbound Forge: spend the bank on the three gear tracks."""
        box = pygame.Rect(90, 70, cfg.SCREEN_WIDTH - 180, cfg.SCREEN_HEIGHT - 230)
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        panel.fill((14, 16, 24, 238))
        self.screen.blit(panel, box.topleft)
        pygame.draw.rect(self.screen, cfg.SMITH_COLOR, box, 2, border_radius=8)

        self.screen.blit(self.font.render("THE SUNBOUND FORGE", True, cfg.SMITH_COLOR),
                         (box.x + 22, box.y + 16))
        bank = f"bank:  Karcite {self.banked['karcite']}   Coin {self.banked['coin']}"
        b = self.font.render(bank, True, cfg.LOOT_COLOR)
        self.screen.blit(b, (box.right - b.get_width() - 22, box.y + 16))

        y = box.y + 58
        for i, track in enumerate(prog.GEAR):
            tier = self.progress.tier(track.key)
            cost = self.progress.next_cost(track.key)
            selected = i == self.forge_index
            row = pygame.Rect(box.x + 14, y - 6, box.width - 28, 74)
            if selected:
                pygame.draw.rect(self.screen, (32, 36, 50), row, border_radius=6)
                pygame.draw.rect(self.screen, cfg.SMITH_COLOR, row, 1, border_radius=6)

            pips = "#" * tier + "." * (track.max_tier - tier)
            head = f"{'>' if selected else ' '} {track.name}  [{pips}]"
            self.screen.blit(self.font.render(head, True, cfg.TEXT_COLOR),
                             (box.x + 24, y))
            if cost is None:
                right, colour = "MASTERWORK", cfg.SMITH_COLOR
            else:
                right = f"{cost['karcite']} Karcite  {cost['coin']} Coin"
                colour = (cfg.LOOT_COLOR if self.progress.can_afford(track.key)
                          else cfg.HP_EMPTY)
            r = self.font.render(right, True, colour)
            self.screen.blit(r, (box.right - r.get_width() - 24, y))

            effect = (track.describe(tier) if tier else track.blurb)
            self.screen.blit(self.small.render(effect, True, cfg.DIM_TEXT),
                             (box.x + 40, y + 26))
            if cost is not None:
                nxt = f"next: {track.describe(tier + 1)}"
                self.screen.blit(self.small.render(nxt, True, cfg.XP_COLOR),
                                 (box.x + 40, y + 44))
            y += 84

        keys = "[W/S] choose   [ENTER] forge it   [E] step away"
        self.screen.blit(self.small.render(keys, True, cfg.DIM_TEXT),
                         (box.x + 24, box.bottom - 28))

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
        returning = (self.progress.level > 1 or any(self.progress.gear.values())
                     or any(self.progress.banked.values()))
        for i, line in enumerate([
            "A Delver's Tale  ·  v1.1 — the haul matters",
            "",
            "Raid the Drownways. Crack the crabs. Climb out with your haul.",
            "Die, and you lose what you carried — never what you learned.",
            "",
            "Press ENTER to begin   ·   ESC to quit",
        ]):
            self._text(line, self.font, cfg.TEXT_COLOR, (cx, 250 + i * 30))
        if returning:
            self._text(
                f"Delver Lv {self.progress.level}  ·  banked "
                f"K{self.progress.banked['karcite']} C{self.progress.banked['coin']}"
                f"  ·  {self._gear_line()}",
                self.small, cfg.DIM_TEXT, (cx, 450))

    def _draw_death(self):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 10, 16, 180))
        self.screen.blit(overlay, (0, 0))
        cx = cfg.SCREEN_WIDTH // 2
        self._text("You fall.", self.big, cfg.HP_COLOR, (cx, 240))
        self._text("Your haul is lost to the deep.", self.font, cfg.TEXT_COLOR, (cx, 310))
        self._text("What you learned, you keep.", self.small, cfg.XP_COLOR, (cx, 340))
        self._text("Press ENTER to wake in Larkhollow", self.font, cfg.DIM_TEXT, (cx, 376))
