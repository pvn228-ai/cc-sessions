# STORYBOOK
*Living story bible & memory file. We add to this as canon is decided.*

> Working title: **THE GROOVE** *(or: Carcinion / The Unturned / Driftward — undecided)*
> Genre: top-down action-RPG → town-founding → military campaign.
> Tone: **melancholy / mythic** — quiet, lonely, the archaeology of a dying world.

---

## THE ONE-LINE PITCH
The world always becomes crab. It has happened before; it is happening again.
You are the first person who refuses to sink with it — so you build a town,
raise an army of the still-human, and descend through three drowned ages to kill
the thing at the bottom that turns everything into crab.

---

## THE COSMOLOGY — three layers, three ages

The three dimensions aren't "ground, basement, sub-basement." They are **eras of
the world, stacked by time.** The world *sinks*: every few hundred years an entire
age is swallowed downward into the dark, a new surface forms over its grave, and
the cycle begins again. To go down is to go **backward through time**, toward the
origin of everything.

- **SURFACE — the living world.**
  Towns, fields, harvests, people who plow over ruins without knowing what sleeps
  beneath them. Bright, ordinary, fragile, and in denial. *Your home layer.*

- **LOWER — the previous world (dungeons).**
  The age that sank last. Its "dungeons" are really its *buildings* — flooded
  temples, collapsed cities, libraries gone to silt. Recognizably human, but
  wrong. Its people are still here. They are still molting.

- **ABYSS — the world before people (or before the sun).**
  The oldest and least human. Whatever fell first has had the longest to *finish*.
  This is the source — the pressure, the pull, the thing that calls everything home.

---

## KRAGGONOTH — first-born of the Karcons *(the villain, the head honcho)*

He was a **regular crab** in the deep of the Brine. Nameless, mindless, one of
uncountable millions on the black floor of the world.

Then the sky broke. A **comet fell into the ocean** and shattered on the deep,
and from its heart spilled a **glowing element** — a light that does not belong in
this world. It found him first. It poured into his shell and it did not kill him;
it *woke* him. It gave him a **mind**, and then it gave him **power**, and then it
gave him a **hunger that has no bottom.** The first crab to ever *think* — and the
first thought he ever had was: *all of this should be mine, and all of it should be
like me.*

He took a name no crab had ever needed: **KRAGGONOTH.**

He is **first-born of the Karcons** — patient zero, war-king, and would-be god in
one. And he is not finished. From the deep he **summons, still** — reaching for
every crustacean the element can touch and **imbuing** it, waking it, twisting it
into a soldier of his host. Every age the light spreads a little higher. Every age
he summons a little more. The army is not marching *toward* completion — it is
*being born,* endlessly, right now, faster than ever.

- **What he wants:** not destruction — *conversion.* A single, silent, perfect
  world, all of it carapace, all of it him. The Groove given a throne.
- **What makes him terrible:** he was the first thing in creation to be *lonely,*
  and his answer to loneliness is to make everything else into himself.
- **Where he is:** the bottom of the **Abyss**, around the buried comet-heart,
  closest to the element, oldest and most imbued. The final descent. The last boss.

---

## THE KARCONS — the imbued host

The **Karcons** are crustaceans — mostly crabs — flooded with the comet's element
and woken into Kraggonoth's army. Imbued = mutated, hardened, enlarged, and bent to
his will. They are the **glow made flesh and claw.**

The element pools deepest at the bottom, so **proximity to the comet-heart = power.**
This gives us our difficulty curve *for free*:
- **Surface Karcons** — faintly glowing, barely-changed scuttlers; the spillover.
- **Lower Karcons** — fully imbued warriors; claw-knights, the **Molted** (last age's
  people the element has half-claimed — *grieving, not evil; some can be saved*).
- **Abyss Karcons** — monstrous, ancient, near-Kraggonoth in might; the Drowned Court.

---

## KARCITE — the comet element *(locked)*
The glowing element is the engine of everything: the mutation, the summoning,
Kraggonoth's mind, the slow turning of the world. It fell once, long ago, into the
deepest dark, and it has seeped upward through the ages ever since. *That upward
seep is why the world turns to crab from the bottom up, and why the surface's time
is finally running out.*

- **Looks:** a cold, pale-green glow inside black meteoric stone; veins of it run
  through the deep rock and pulse faintly, like something breathing.
- **What it does to crustaceans:** imbues — wakes, mutates, enlarges, enlists. The
  raw fuel of the Karcon host. This is what Kraggonoth reaches *through* to summon.
- **What it does to everything else:** the Groove — forces flesh slowly toward the
  old shape. (This is the seed of the player's personal-carcinization curse.)
- **What it does for YOU — the economy keystone:** refined, Karcite is power.
  Delvers mine it from the deep; your town **refines** it; you forge it into
  **weapons, walls, and troops.** The cruel irony of the war: *the only thing strong
  enough to arm the Unturned is the same light that makes the Karcons.* Using it
  risks turning. Every upgrade is a bargain with the enemy's own substance.
  - raw **Karcite** (mined) → refined **Brightstone/ingots** (town) → gear & troops.
  - deeper layers yield richer Karcite — so the war economy *pulls you downward,*
    straight toward Kraggonoth. The map and the economy point the same way.

---

## WORLD GENERATION — authored Surface, procedural depths

- **SURFACE — authored & persistent.** Hand-built area-graph: your towns, your
  base, fixed geography, the world you defend. It never regenerates. *(This is the
  `world_data` map we already prototyped.)*
- **LOWER & ABYSS — procedurally generated.** Each descent builds a fresh
  area-graph from a seed. Reuses the same engine we already have (screen-sized
  areas linked at borders); the generator just *produces* the area layout, tiles,
  enemies, and Karcite/loot instead of reading them from a file.

### Entry points are the dial
You descend through **entrances** on the Surface (sinkholes, ruins, a Delvers'
lift). **The entrance defines the run** it generates:

- **Length / Depth** — how many area-levels deep it goes (how far toward the Abyss).
- **Size / Breadth** — how sprawling each level is (how many areas per level).
- **Danger** — enemy tier & density, which scales with depth.
- **Richness** — Karcite/ore/gold yield, also scaling with depth.
- **Theme** — tileset & room templates (Lower = drowned cities of the last age;
  Abyss = older, organic, alien, crab).

So a small surface crack = a short, shallow, low-risk dig; a yawning ruin-mouth =
a long, deep, deadly expedition that may break through into the **Abyss** at the
bottom. **Bigger mouth → longer, deeper, richer, deadlier.** The player reads the
entrance and *chooses the expedition's scale.*

### Generator unit — branching levels, D2 Cloister style *(decided)*
A descent is a stack of **levels**; each level is a **branching cluster of our
screen-sized areas**, generated like a Diablo II Cloister/Catacombs:

- **One entrance** (the stairs you came down) and **one exit** — the **down-stairs**
  to the next level, sitting at the end of exactly **one** branch.
- The level **branches out** into multiple arms; **only one arm is "right"** (holds
  the down-stairs). The rest are **dead-ends** — but they're where the **loot,
  Karcite veins, ore, side-encounters, and optional mini-bosses** live.
- So every level is a **risk/greed choice:** make a beeline for the stairs, or sweep
  the dead-ends for resources and eat the danger/time.

**Mapping to entry-point dials:**
- **Length / Depth** = number of stacked levels (more levels → closer to the Abyss).
- **Size / Breadth** = how many areas per level & how much it branches (bushier
  cluster = more dead-ends = more loot & more risk).
- The Abyss is just the deepest levels with the Abyss theme/enemy/richness tables —
  reached when a deep enough entrance's stairs finally break through.

*(Implementation: generate a graph of areas per level — pick a path of N areas for
the critical route, attach M dead-end branches, place the down-stairs at the path's
end, scatter loot/Karcite weighted toward the dead-ends. Areas still link at
borders exactly as the Surface does.)*

### Generation flavor (keep the melancholy)
Use **room/area templates** per theme so the depths feel *built, then drowned*, not
random noise — flooded temple halls, collapsed libraries, streets under silt in the
Lower; cave-cathedrals and chitin growths in the Abyss. Procedural *arrangement* of
authored *pieces*.

### Persistence — dungeons regenerate; you hold only your town(s) *(decided)*
**Dungeons cannot be claimed, garrisoned, or held.** They are the enemy's ground.
Every descent **regenerates** (D2-style) — fresh branches, fresh loot, endless
Karcite. You go down to *take*, not to *keep*; you always come back up.

**The player owns one or two Surface towns — nothing else.**
- **Town #1 — your home/refuge.** Where everything lives: smelter, refinery,
  barracks, walls, the Unturned you've gathered. The heart you defend.
- **Town #2 (optional, later) — a forward base** nearer a great Abyss-mouth, staged
  for the endgame assault. A reason to *have* a second town, not just more sprawl.
- Other Surface settlements exist but are **NPC-owned** — trade, recruit, quests,
  not yours to govern.

This reframes the war: you don't conquer the underworld, you **survive expeditions
into it** and **defend your town(s) on the Surface**, until you're strong enough for
the one-way march to the bottom.

---

## RESOURCES & CRAFTING — the world economy

Two tiers of material: **mundane** (what builds a town and arms a militia) and
**Karcite** (the dangerous magic on top). You gather raw, refine at town
buildings, and craft up into goods, gear, and troops.

### The six world resources
| resource | gathered from | refines into | used for |
|---|---|---|---|
| **Wood** | forests (Surface) | planks, **charcoal** (smelting fuel) | buildings, shafts, bows, scaffolding |
| **Stone** | quarries / deep rock | blocks, **mortar** (w/ lime) | walls, foundations, roads, whetstones |
| **Flax** | farmed fields (Surface) | fiber → thread → **linen cloth**, **rope** | padding/gambeson, sails, bandages, bowstrings |
| **Iron** | ore, mined (Lower-rich) | **iron ingots** (ore + charcoal) | weapons, armor, tools, nails, hinges |
| **Copper** | ore, mined (shallow→Lower) | **copper ingots** | early tools, fittings, **Karcite conduits** |
| **Gold** | deep veins / rivers (deepest) | **gold ingots**, **coin** | currency & trade — *and tempering Karcite (see below)* |

### Crafting flows (raw → intermediate → item)
- **Wood** → planks (build) / charcoal (the fuel everything smelts with).
- **Stone** → blocks + mortar → walls & buildings (the town's defense).
- **Flax** → fiber → thread → linen → **gambeson** (armor padding) & **rope** &
  **bowstrings**. Soft economy, but every soldier needs it.
- **Iron** ore + charcoal → ingots → **arms & armor** (the militia's backbone).
- **Copper** ore + charcoal → ingots → cheap tools early; later, **conduits** that
  carry Karcite safely through a weapon or wall.
- **Gold** → coin (buy/sell/recruit) **and the key trick below.**

### The clever knot — gold tempers Karcite *(ties economy → curse → boss)*
Raw **Karcite** makes the strongest gear in the game, but wielding it **spreads the
Groove** — your troops (and you) slowly start to turn. **Gold + copper conduits can
*temper* Karcite,** binding the glow so it empowers without corrupting — at a cost,
because gold is the rarest, deepest resource.

So the whole economy becomes a **moral dial**: cheap raw-Karcite gear = strong now,
turning later; gold-tempered gear = safe but expensive and slow. *The more war you
wage, the deeper you must mine, the closer you get to Kraggonoth — exactly as he
wants.*

---

## THE LAW OF CARCINIZATION — *the world's grain, now lit by the element*
> The comet's element is the **physical cause** of the Groove: it forces living
> things into the old shape, faster and more completely the more of it touches them.
> The myth below is *why it works* — the element only had to nudge a world that was
> already leaning crab-ward.


In the **First Age** there was no land. Only the **Brine**: a black, sunless,
bottomless sea. The first life was small and soft and many-legged, and the sea
taught its children one lesson, over and over, for uncountable years:

> *To survive pressure — grow a shell.
> To survive teeth — grow claws.
> To survive everything — become a crab.*

The Brine carcinized its children so many times that **crab stopped being a shape
and became a destiny** — a groove worn so deep into the bones of the world that
all life, given enough time and enough pressure, *slides into it.*

Then light came. The Brine receded, land rose, and soft new things — grass,
beasts, people — grew up high and dry, far from the pressure, free of the groove.
They forgot the sea. They built the first cities on the new land and called it the
whole world.

**But the Brine never died. It only sank, and waited — because pressure is
patient.** Every age the land grows heavy with the works and bones of those who
live on it, and that weight presses down, and one night the world *sinks*: a whole
age delivered back to the sea to be remade in the old shape. The drowned age
becomes the new floor. New land forms above. Inhale, the land rises. Exhale, it
sinks. The cycle is the world *breathing.*

**So the crab army is not an invasion. It is the world's true form reasserting
itself.** Everything the Brine reclaims, it returns to the groove. The deeper you
go, the more complete the turning:

- On the **Surface**, the carcinization is a rumor — hard patches on a farmer's
  skin, tide-lines where there is no sea, children dreaming of claws.
- In the **Lower** dwell the **Molted** — the last age's people, faces still
  half-human under fresh chitin. They are not monsters. They are *grieving.*
- In the **Abyss** are the fully-turned, and the things that were always crab —
  and at the very bottom, the first crab, the groove given a will: **the
  CARCINION.** The Pearl in the Mother. The shape the world is falling toward.

---

## WHY NOW — the sinking is early

The next sinking is overdue, and the signs are everywhere. The **Delvers' Guild**
has always descended to study and rob the lost ages — but this time a delver
(you) goes down and finds the Lower *rising.* The crabs are **climbing.** The
Carcinion isn't waiting for the world to sink on its own schedule. It is sending
the Host **up** to drag the surface down early.

You can't just delve anymore. You have to **hold ground.**

---

## YOU — a human teenager *(at first)*
You begin as an **ordinary human teen** from a **Greenward** village — a Delvers'
Guild **initiate**, too young for a real descent, who gets pulled into one anyway
when the signs start and an elder doesn't come back up. Coming-of-age is the spine
of the *character* the way descent is the spine of the *world.*

Why a teen matters:
- **The Turning hits harder.** It's your *youth* calcifying — the body-horror is
  personal and unfair in a way it wouldn't be for a grizzled veteran.
- **You grow on every axis** — skill, the role you carry (initiate → delver →
  founder of Larkhollow → commander of the Unturned), and how the world treats you.
- *"At first"* is a promise: who/what you become by the Brinedeep is an open thread
  (older, hardened, half-turned, or something the Brine has never seen).

## THE ARC — Delver, then Founder, then Commander
The campaign arc, which is also the genre arc:

1. **DELVER (action-RPG).** Alone. Sword, exploration, the first horror of meeting
   a Molted that says your name.
2. **FOUNDER (town-building).** You claim the last dry place and make it a refuge
   for the **Unturned** — humans, beasts, and even Molted who fought the groove and
   partly won. You rebuild, recruit, equip.
3. **COMMANDER (military).** You raise troops and do what no age has ever done:
   *refuse to sink.* You can't hold the depths — so you **defend your town(s) on the
   Surface** and **raid downward** for Karcite and strength, until you're ready for
   the one-way **assault on the Abyss** to put a blade in the first crab.

---

## THE TWIST SEEDS *(melancholy / mythic — earn the sadness)*
- **The Molted can be saved.** Some. Carcinization is a slow death of *self*, not a
  monster factory. Recruiting a half-turned soldier means racing their clock.
- **You carry the groove too.** Going deep accelerates your own turning — a mark
  that spreads. The town and the surface are where you heal it back. The deeper the
  war goes, the more you risk becoming the thing you fight.
- **The bottom truth.** Stopping the sinking may doom the surface another way — the
  weight has to go *somewhere.* Maybe the only mercy is to choose what sinks.

---

## COMBAT — directional swing + crack-the-shell *(locked: core feel)*

**Base:** top-down, **face a direction and swing** (Zelda / Hyper Light Drifter).
Fast, readable, no auto-aim — you hit the arc in front of you. But every enemy is a
**crab**, so the depth comes from the one thing they all have: **a shell and raised
claws.** You don't just trade hits — you *open* them up.

**The signature loop — shells & guard:**
- **Frontal guard.** Karcons face you claws-up. A swing into a raised guard **chips
  for little and bounces you** — mashing the front is a trap.
- **Open the opening.** Two clean answers, both about *positioning and timing*:
  1. **Flank it** — strike the **side/back** (soft joints) for full damage. Rewards
     movement, kiting, dashing *through* an attack to its blind side.
  2. **Punish the claw** — when it **raises a claw to attack**, the guard drops; hit
     the window. Rewards reading tells (light parry/bait feel, no hard parry timing).
- **Crack the carapace.** Bigger Karcons need their **shell broken first**: land
  hits / a charged **Shellbreaker** to crack the plate, exposing flesh and a
  **stagger window** of bonus damage (Monster-Hunter-part-break, but lightweight).

**The kit (small, expressive):**
- **Light swing** — fast directional arc, cheap. Your bread and butter.
- **Heavy / charged "Shellbreaker"** — slow wind-up, breaks guard & cracks shell;
  costs stamina, leaves you exposed. Commitment.
- **Dash / roll** — i-frames + the repositioning tool; how you get to the flank.
- **Stamina** — light, governs Heavy + Dash (so you can't just spam openings).
- **Karcite weapons add a verb** — e.g. a glow-edge that *ignores* guard but feeds
  the Turning; gold-tempered (Sunbound) versions soften that cost. Combat plugs
  straight into the economy/curse.

**Teen flavor:** nimble over strong — you start dash-light and slappy, more about
**reading and dancing around claws** than out-muscling them. Power (and weight)
comes from gear and growth.

## NAMING TABLE *(remaining candidates — most things now locked above)*
| thing | candidates |
|---|---|
| The villain (final boss) | **KRAGGONOTH** — *locked* |
| The enemy army | the **KARCONS** — *locked* |
| The comet element (raw) | **KARCITE** — *locked* |
| Karcite refined / tempered | **Brightstone** (refined) · **Sunbound Brightstone** (gold-tempered) — *locked* |
| The primal sea / element source | the **Brine** — *locked* |
| The curse / law | the **Turning** (folk: "going crab," "the crabbing") — *locked* |
| Surface (in-world name) | the **Greenward** — *locked* |
| Lower (in-world name) | the **Drownways** — *locked* |
| Abyss (in-world name) | the **Brinedeep** — *locked* |
| Surface Karcons (tier 1) | **Pinchlings** — *locked* |
| Lower Karcons (tier 2) | the **Molted** — *locked* |
| Abyss Karcons (tier 3) | the **Drowned Court** — *locked* |
| Your faction | the **Unturned** (guild: the **Delvers' Guild**) — *locked* |
| Home town | **Larkhollow** — *locked* |
| Forward base (optional, later) | **Deepgate** — *locked* |

---

## CANON DECIDED SO FAR
- Genre: top-down ARPG → found a town → military campaign. *(player goal: build town + troops)*
- Three layers are **ages stacked by time**; descending = going back in time.
- Antagonist army: the **KARCONS** — mutant crustaceans (mostly crabs).
- Final boss: **KRAGGONOTH**, first-born of the Karcons.
- Origin engine: a **comet fell into the sea**; its element **KARCITE** woke a
  regular crab into Kraggonoth (mind + power) and **imbues** crustaceans into Karcons.
  He summons the host still, from the Abyss, endlessly.
- **Karcite** is the physical cause of **carcinization** (the Groove); it seeps up
  from the deep over ages — deeper = more imbued = stronger.
- **World resources:** Wood, Stone, Flax, Iron, Copper, Gold — gathered, refined,
  and crafted into goods/gear/troops. **Karcite** is the rare magic tier on top.
- **Economy as moral dial:** raw Karcite = strong-but-corrupting; **gold + copper
  conduits temper it** (safe but costly). War pulls the player deeper, toward Kraggonoth.
- **World gen:** Surface is authored & persistent; **Lower & Abyss are procedurally
  generated.** **Entry points set the run's length/depth, size, danger, richness** —
  bigger mouth → longer, deeper, richer, deadlier. Generation = procedural
  arrangement of authored room templates per theme.
- **Persistence:** dungeons **can't be claimed** — they **regenerate** every descent
  (raid, don't hold). Player owns **only 1–2 Surface towns** (home + optional forward
  base); other settlements are NPC-owned.
- **Military arc:** defend your town(s), raid the depths for Karcite/strength, then a
  one-way assault on the Abyss. No territory-holding underground.
- **Names locked:** Brine, the Turning, Greenward/Drownways/Brinedeep,
  Pinchlings/Molted/Drowned Court, the Unturned + Delvers' Guild, Larkhollow,
  Deepgate, Brightstone/Sunbound Brightstone.
- **Protagonist:** a **human teenager**, Delvers' Guild initiate (coming-of-age).
- **Combat:** top-down **directional swing** + **crack-the-shell** — flank or punish
  the raised claw; Shellbreaker cracks armor for a stagger window; light/heavy/dash
  + stamina. Naming/tone whimsical-fantasy over a melancholy world.
- Tone: melancholy / mythic, whimsical names.

## OPEN QUESTIONS *(for next conversation)*
- [x] Generator unit: **branching multi-area levels, D2 Cloister style.** *(decided)*
- [x] Lock remaining names. *(done)*
- [x] Player identity: **human teen, guild initiate.** *(decided)*
- [x] Combat kind: **directional swing + crack-the-shell.** *(decided)*
- [ ] Does the personal-Turning curse mechanic go in v1, or later?
- [ ] Tone check: how dark do the Molted get — pitiable, or genuinely frightening?
- [ ] Kraggonoth — does the player ever *meet* him before the end (taunts, a herald)?
- [ ] Sketch the opening 10 minutes (the inciting delve).
- [ ] **Start building:** convert the prototype to top-down + combat + first town?
