"""Everything the delver keeps between runs: the bank, XP/levels, and gear.

The v1 slice proved the loop (descend -> raid -> return). This is the part that
makes the haul *matter*: Karcite and coin you climb out with are banked, spent at
the Sunbound Forge in Larkhollow on three gear tracks, and every Karcon you put
down feeds XP toward a level. Loot is lost on death; **levels and gear are not** —
what you already carried home is yours.

``Progress`` is the single source of truth for the player's derived stats, so the
Player asks it for damage/HP/dash numbers instead of reading the raw constants.
A fresh ``Progress()`` reports exactly the v1 base values, so nothing changes
until you actually spend something.
"""

import json
import os
from pathlib import Path

from . import settings as cfg


# --------------------------------------------------------------------- gear
class GearTrack:
    """One upgrade line at the Forge: a name, a flavour line, and its cost curve."""

    def __init__(self, key, name, blurb, max_tier, karcite, coin, describe):
        self.key = key
        self.name = name
        self.blurb = blurb
        self.max_tier = max_tier
        self._karcite = karcite      # cost of the FIRST tier
        self._coin = coin
        self._describe = describe    # tier -> short effect string

    def cost(self, tier):
        """Cost to buy ``tier`` (1-based). Each tier costs more than the last."""
        step = tier - 1
        return {"karcite": self._karcite + 3 * step, "coin": self._coin + 4 * step}

    def describe(self, tier):
        return self._describe(tier)


_BOOT_COST_STEP = 6      # stamina shaved off a dash per Tidestep tier
_BOOT_CD_STEP = 5        # frames shaved off the dash cooldown per tier

GEAR = [
    GearTrack(
        "blade", "Honed Edge",
        "A keener bite — every swing, every Shellbreaker.",
        3, 4, 6,
        lambda t: f"+{t} damage on all attacks",
    ),
    GearTrack(
        "ward", "Sunbound Ward",
        "Gold-tempered. The purple glow burns slower through it.",
        3, 5, 4,
        lambda t: f"+{t} max heart{'s' if t != 1 else ''}, Searing ticks {t * 50}% slower",
    ),
    GearTrack(
        "boots", "Tidestep Boots",
        "Get behind the claw before it finds you.",
        3, 3, 5,
        lambda t: f"dash costs {cfg.DASH_COST - _BOOT_COST_STEP * t} stamina, "
                  f"recovers {_BOOT_CD_STEP * t} frames sooner",
    ),
]

GEAR_BY_KEY = {g.key: g for g in GEAR}

# XP needed to reach the next level, from level 1 upward.
XP_BASE = 12
XP_GROWTH = 1.6

# What a felled Karcon is worth.
XP_PINCHLING = 5
XP_CLAWKNIGHT = 16


def save_path():
    """Where the run-to-run save lives (override with ``LARKHOLLOW_SAVE``)."""
    env = os.environ.get("LARKHOLLOW_SAVE")
    if env:
        return Path(env)
    return Path.home() / ".larkhollow" / "save.json"


class Progress:
    """Persistent delver state: bank, level, gear tiers."""

    def __init__(self):
        self.banked = {"karcite": 0, "coin": 0}
        self.level = 1
        self.xp = 0
        self.gear = {g.key: 0 for g in GEAR}

    # ------------------------------------------------------------ derived stats
    @property
    def max_hp(self):
        # A level is a heart; the Ward is more.
        return cfg.PLAYER_MAX_HP + (self.level - 1) + self.gear["ward"]

    @property
    def stamina_max(self):
        return cfg.STAMINA_MAX + 8 * (self.level - 1)

    @property
    def swing_damage(self):
        return cfg.SWING_DAMAGE + self.gear["blade"]

    @property
    def heavy_damage(self):
        return cfg.HEAVY_DAMAGE + self.gear["blade"]

    @property
    def plunge_damage(self):
        return cfg.PLUNGE_DAMAGE + self.gear["blade"]

    @property
    def dash_cost(self):
        return max(8, cfg.DASH_COST - _BOOT_COST_STEP * self.gear["boots"])

    @property
    def dash_cooldown(self):
        return max(4, cfg.DASH_COOLDOWN - _BOOT_CD_STEP * self.gear["boots"])

    @property
    def searing_interval(self):
        """Frames of immunity after a Searing tick — the Ward stretches them."""
        return int(cfg.SEARING_INTERVAL * (1 + 0.5 * self.gear["ward"]))

    # -------------------------------------------------------------------- XP
    @property
    def xp_to_next(self):
        return int(XP_BASE * XP_GROWTH ** (self.level - 1))

    def add_xp(self, amount):
        """Bank XP. Returns the number of levels gained (0 usually)."""
        if amount <= 0:
            return 0
        self.xp += amount
        gained = 0
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            gained += 1
        return gained

    # ------------------------------------------------------------------ bank
    def bank(self, loot):
        for kind, value in loot.items():
            self.banked[kind] = self.banked.get(kind, 0) + value

    # ------------------------------------------------------------- the forge
    def tier(self, key):
        return self.gear[key]

    def next_cost(self, key):
        """Cost of the next tier of ``key``, or None if it is maxed."""
        track = GEAR_BY_KEY[key]
        tier = self.gear[key] + 1
        if tier > track.max_tier:
            return None
        return track.cost(tier)

    def can_afford(self, key):
        cost = self.next_cost(key)
        if cost is None:
            return False
        return all(self.banked.get(k, 0) >= v for k, v in cost.items())

    def buy(self, key):
        """Spend the bank on the next tier. Returns True if the forge took it."""
        if not self.can_afford(key):
            return False
        for k, v in self.next_cost(key).items():
            self.banked[k] -= v
        self.gear[key] += 1
        return True

    # ------------------------------------------------------------ persistence
    def to_dict(self):
        return {"banked": dict(self.banked), "level": self.level, "xp": self.xp,
                "gear": dict(self.gear)}

    @classmethod
    def from_dict(cls, data):
        p = cls()
        banked = data.get("banked") or {}
        p.banked = {"karcite": int(banked.get("karcite", 0)),
                    "coin": int(banked.get("coin", 0))}
        p.level = max(1, int(data.get("level", 1)))
        p.xp = max(0, int(data.get("xp", 0)))
        gear = data.get("gear") or {}
        for g in GEAR:
            p.gear[g.key] = max(0, min(g.max_tier, int(gear.get(g.key, 0))))
        return p

    def save(self):
        path = save_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.to_dict(), indent=2))
            return True
        except OSError:
            return False    # a read-only home is not worth crashing a run over

    @classmethod
    def load(cls):
        """Load the save, or a fresh delver if there isn't one (or it's junk)."""
        path = save_path()
        try:
            return cls.from_dict(json.loads(path.read_text()))
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()
