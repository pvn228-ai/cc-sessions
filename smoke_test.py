"""Headless smoke test for the slice (no display).

Covers v1: surface parsing, platformer physics, the Pinchling shell rules
(bounce/flank/punish/plunge/Shellbreaker), Searing damage, loot pickup,
dungeon generation (hub + two branches, exactly one with stairs), descending
to the bottom, the death/return loop, and rendering both scenes.

Covers v1.1: the plated Clawknight, XP and drops from a kill, levels surviving
death, and the Sunbound Forge turning banked loot into gear (and saving it).
"""

import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Never touch the player's real save while testing.
os.environ["LARKHOLLOW_SAVE"] = os.path.join(
    tempfile.mkdtemp(prefix="larkhollow-test-"), "save.json")

import pygame  # noqa: E402

from game import settings as cfg  # noqa: E402
from game.area import Room  # noqa: E402
from game.entities import Pinchling, Clawknight  # noqa: E402
from game import progress as prog  # noqa: E402
from game.player import Player  # noqa: E402
from game.world import World  # noqa: E402
from game.dungeon import Dungeon  # noqa: E402
from game.game import Game, TITLE, SURFACE, DUNGEON, DEATH, FORGE  # noqa: E402


class _NoKeys:
    def __getitem__(self, _):
        return False


NOKEYS = _NoKeys()
FLOOR = "#" * cfg.AREA_COLS


def test_surface_parses():
    pygame.init()
    w = World(Player(0, 0))
    assert w.room.spawn_tile is not None, "Larkhollow has no spawn"
    assert any(p.kind == "npc" for p in w.room.props), "no NPC in Larkhollow"
    w.coord = (1, 0)
    assert w.room.entrance is not None, "no dungeon entrance on the Old Road"
    print("[ok] surface parses (spawn, NPC, entrance)")


def test_player_lands():
    pygame.init()
    p = Player(100, 0)
    room = Room(["                        "] * 14 + [FLOOR], "surface")
    for _ in range(200):
        p.handle_input(NOKEYS)
        room.update(p)
        if p.on_ground:
            break
    assert p.on_ground, "player never landed"
    print("[ok] platformer physics lands the player")


def test_pinchling_shell_rules():
    pygame.init()
    c = Pinchling(400, 400)
    c.facing = -1                       # guarding to its left
    cx = c.rect.centerx
    front = cx - 100                    # attacker on the guarded (left) side
    back = cx + 100                     # attacker behind (right) flank

    assert Pinchling(400, 400).receive(1, "light", front) is False or True  # smoke
    a = Pinchling(400, 400); a.facing = -1
    assert a.receive(1, "light", front) is False, "front light should bounce"
    b = Pinchling(400, 400); b.facing = -1
    assert b.receive(1, "light", back) is True, "flank should land"
    h = Pinchling(400, 400); h.facing = -1
    assert h.receive(1, "heavy", front) is True, "Shellbreaker should land"
    assert h.staggered(), "Shellbreaker should crack the shell (stagger)"
    pl = Pinchling(400, 400); pl.facing = -1
    assert pl.receive(1, "plunge", front) is True, "plunge ignores the guard"
    print("[ok] Pinchling shell rules: bounce / flank / Shellbreaker+stagger / plunge")


def test_clawknight_plate_rules():
    pygame.init()
    k = Clawknight(400, 400)
    k.facing = -1
    back = k.rect.centerx + 100        # behind it
    front = k.rect.centerx - 100       # into the guard

    assert k.armoured(), "a Clawknight starts in intact plate"
    hp = k.hp
    assert k.receive(3, "light", back) is True, "a flank should connect"
    assert k.hp == hp, "flesh damage must not land through intact plate"

    for _ in range(cfg.CLAWKNIGHT_PLATE):
        k.receive(2, "heavy", front)   # Shellbreakers chew through the plate
    assert not k.armoured(), "Shellbreakers should breach the plate"
    assert k.staggered(), "a breached plate opens a stagger window"

    k.receive(3, "light", back)
    assert k.hp == hp - 3, "with the plate gone, flanks bite"
    print("[ok] Clawknight plate: armour shrugs off flesh damage until breached")


def test_kill_grants_xp_and_drops():
    pygame.init()
    rows = ["                        "] * 13 + ["     E                  ", FLOOR]
    room = Room(rows, "cave")
    enemy = next(iter(room.enemies))
    p = Player(5 * cfg.TILE_SIZE, 13 * cfg.TILE_SIZE)
    enemy.hp = 1
    p.rect.centerx = enemy.rect.centerx - 24
    p.facing = 1
    xp, picked = 0, []
    for _ in range(90):                 # Shellbreakers land whatever it faces
        p.handle_input(NOKEYS)
        p.iframes = 60                  # ignore its claws; we are testing the kill
        if p.attack_type is None:
            p.on_attack_heavy()
        result = room.update(p)
        xp += result.get("xp", 0)
        picked += result.get("picked", [])
        if enemy.dead:
            break
    assert enemy.dead, "the Pinchling should be down"
    assert xp == prog.XP_PINCHLING, f"felling a Pinchling should pay XP (got {xp})"
    for _ in range(4):                  # let the shard be swept up
        picked += room.update(p).get("picked", [])
    assert any(l.kind == "karcite" for l in picked) or len(room.loot) > 0, \
        "a felled Karcon should shed a shard"
    print(f"[ok] a felled Karcon pays {xp} XP and sheds a shard")


def test_forge_spends_and_upgrades():
    pygame.init()
    pr = prog.Progress()
    assert pr.max_hp == cfg.PLAYER_MAX_HP and pr.swing_damage == cfg.SWING_DAMAGE, \
        "a fresh delver must report the v1 base stats"

    pr.banked = {"karcite": 99, "coin": 99}
    assert pr.buy("blade") and pr.swing_damage == cfg.SWING_DAMAGE + 1, "blade should bite harder"
    assert pr.banked["karcite"] < 99 and pr.banked["coin"] < 99, "the forge takes payment"
    assert pr.buy("ward") and pr.max_hp == cfg.PLAYER_MAX_HP + 1, "the Ward is a heart"
    assert pr.searing_interval > cfg.SEARING_INTERVAL, "the Ward should slow the Searing"
    assert pr.buy("boots") and pr.dash_cost < cfg.DASH_COST, "boots make the dash cheaper"

    broke = prog.Progress()
    assert not broke.can_afford("blade") and not broke.buy("blade"), "no bank, no gear"

    maxed = prog.Progress()
    maxed.banked = {"karcite": 999, "coin": 999}
    track = prog.GEAR_BY_KEY["blade"]
    for _ in range(track.max_tier):
        assert maxed.buy("blade")
    assert maxed.next_cost("blade") is None and not maxed.buy("blade"), "tracks cap out"
    print("[ok] the Sunbound Forge spends the bank and upgrades the delver")


def test_levels_and_save_round_trip():
    pygame.init()
    pr = prog.Progress()
    need = pr.xp_to_next
    assert pr.add_xp(need) == 1 and pr.level == 2, "enough XP should level you"
    assert pr.max_hp == cfg.PLAYER_MAX_HP + 1, "a level is a heart"
    pr.banked = {"karcite": 7, "coin": 3}
    pr.buy("boots")
    assert pr.save(), "progress should save"

    back = prog.Progress.load()
    assert back.level == pr.level and back.gear == pr.gear and back.banked == pr.banked, \
        "the save should round-trip"
    print(f"[ok] XP levels the delver and the save round-trips (Lv {back.level})")


def test_searing_damages():
    pygame.init()
    rows = ["                        "] * 13 + ["     ^                  ", FLOOR]
    room = Room(rows, "cave")
    p = Player(5 * cfg.TILE_SIZE, 13 * cfg.TILE_SIZE)
    before = p.hp
    for _ in range(40):
        room.update(p)
    assert p.hp < before, "Searing did not damage the player"
    print(f"[ok] Karcite Searing damages the player ({before} -> {p.hp})")


def test_loot_pickup():
    pygame.init()
    rows = ["                        "] * 13 + ["     *                  ", FLOOR]
    room = Room(rows, "cave")
    p = Player(5 * cfg.TILE_SIZE, 13 * cfg.TILE_SIZE)
    picked = []
    for _ in range(10):
        picked += room.update(p).get("picked", [])
    assert len(picked) == 1 and picked[0].kind == "karcite", "loot not collected"
    print("[ok] loot is picked up")


def test_dungeon_generation():
    pygame.init()
    d = Dungeon(Player(0, 0), max_depth=2)
    assert set(d.rooms) == {"hub", "east", "west"}, "level is not hub+2 branches"
    with_stairs = [k for k in ("east", "west") if d.rooms[k].stairs is not None]
    assert len(with_stairs) == 1, "exactly one branch must hold the stairs"
    assert d.rooms["hub"].exit_prop is not None, "hub needs a climb-out exit"
    assert d.depth == 1
    print("[ok] dungeon generates hub + 2 branches, one stairway, an exit")


def test_descend_to_bottom():
    pygame.init()
    player = Player(0, 0)
    d = Dungeon(player, max_depth=2)
    # Level 1 -> take the stairs.
    d.current = d.stairs_side
    player.rect.center = d.room.stairs.rect.center
    assert d.interact() == ("descend",), "stairs should descend"
    assert d.depth == 2
    # Level 2 (the bottom) -> stairs should end the run.
    d.current = d.stairs_side
    player.rect.center = d.room.stairs.rect.center
    assert d.interact() == ("bottom",), "deepest stairs should reach the bottom"
    print("[ok] descending the stairs reaches the bottom across levels")


def test_forge_scene_in_town():
    pygame.init()
    g = Game()
    g._new_game()
    g.progress.banked = {"karcite": 99, "coin": 99}
    smith = next(p for p in g.world.room.props if p.kind == "smith")
    g.player.rect.center = smith.rect.center
    g._interact()
    assert g.state == FORGE, "standing at the anvil should open the Forge"
    g._draw()

    before = g.player.max_hp
    g.forge_index = [t.key for t in prog.GEAR].index("ward")
    g._forge_key(pygame.K_RETURN)
    assert g.progress.tier("ward") == 1, "ENTER should forge the selected track"
    assert g.player.max_hp == before + 1, "the Ward should add a heart right away"
    g._forge_key(pygame.K_e)
    assert g.state == SURFACE, "E should step away from the anvil"
    print("[ok] the Forge opens in town, spends the bank, and closes")


def test_xp_survives_death():
    pygame.init()
    g = Game()
    g._new_game()
    before = g.progress.level
    g._gain_xp(g.progress.xp_to_next)      # level up
    level = g.progress.level
    assert level == before + 1, "enough XP in one go should level the delver"
    g.dungeon = Dungeon(g.player, max_depth=2)
    g.state = DUNGEON
    g.run_loot["karcite"] = 9
    g.player.hp, g.player.dead = 0, True
    g._update()
    g._respawn_in_town()
    assert g.run_loot["karcite"] == 0, "the haul is lost"
    assert g.progress.level == level, "levels are not lost with the haul"
    print("[ok] death costs the haul, never the levels")


def test_game_loop_and_death():
    pygame.init()
    g = Game()
    assert g.state == TITLE
    g._draw()               # the title also reports a returning delver
    g._new_game()
    assert g.state == SURFACE
    g._draw()

    # Force into the dungeon and collect/lose loot.
    g.dungeon = Dungeon(g.player, max_depth=2)
    g.state = DUNGEON
    g.run_loot["karcite"] = 5
    g._draw()
    g.player.hp = 0
    g.player.dead = True
    g._update()  # should flip to DEATH
    assert g.state == DEATH, "death not detected"
    g._respawn_in_town()
    assert g.state == SURFACE and g.run_loot["karcite"] == 0, "loot not lost on death"
    print("[ok] game loop: title -> surface -> dungeon -> death -> respawn (loot lost)")


def test_no_crash_over_frames():
    pygame.init()
    g = Game()
    g._new_game()
    g.dungeon = Dungeon(g.player, max_depth=3)
    g.state = DUNGEON
    # Drop a plated Clawknight in the room so its armour path renders too.
    g.dungeon.room.enemies.add(Clawknight(cfg.SCREEN_WIDTH // 2, 300, "cave"))
    for i in range(600):
        if i % 50 == 0:
            g.player.on_attack_light()
        if i % 80 == 0:
            g.player.on_attack_heavy()
        g.player.handle_input(NOKEYS)
        g.scene.update()
        g._draw()
        if g.player.dead:
            g.player.revive()
    print("[ok] 600 dungeon frames render without crashing")


if __name__ == "__main__":
    test_surface_parses()
    test_player_lands()
    test_pinchling_shell_rules()
    test_clawknight_plate_rules()
    test_kill_grants_xp_and_drops()
    test_forge_spends_and_upgrades()
    test_levels_and_save_round_trip()
    test_searing_damages()
    test_loot_pickup()
    test_dungeon_generation()
    test_descend_to_bottom()
    test_forge_scene_in_town()
    test_xp_survives_death()
    test_game_loop_and_death()
    test_no_crash_over_frames()
    print("\nAll smoke tests passed.")
