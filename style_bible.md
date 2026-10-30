# Style bible: "blocky game" shorts (Style B)

Measured from the 2 reference videos the user uploaded (both 720x1280, 60 fps, ~50 s):
- **tensec**: "What if MOM gave you 10 seconds of Roblox"
- **momplays**: "What if your MOM started playing Roblox"

Contact sheets (4 fps) were read frame by frame, and pixel colours and sizes were measured on full-resolution frames.
The raw analysis is in `analysis/ref_data/`. Code that draws this style: `animator/style.py` (characters) and `animator/sets.py` (places, props, game UI).

Only the **style** is copied. The reference channel's characters, names, logos, text and sound files are not used.

## 1. Format and safe zones
| What | Value |
|---|---|
| Frame | 720x1280 (9:16). The references are 60 fps; we render 30 fps (motion reads the same) |
| Safe zone (user's Shorts template) | The whole character and key props inside **x 38-680, y 149-1013**; below y 678 only up to x 599 (like/comment buttons). Enforced by `animator/safezone.py` |
| HUD | Timer pill at the top centre, y 150-210 (inside the zone). Shots with a HUD use `top=250`, so characters sit below it |
| Captions | The references burn in big captions at y ≈ 825. **Our default is no captions**; on request, use `assembler/captions.py` (measured look below) |
| Transitions | Mostly **hard cuts**. Plus a few whip pans (motion-blur smear) and white shockwave rings on big cards. No soft dissolves |

### Captions (when the user asks for them; measured from the references)
- **Position:** centred at x 360, y ≈ 825.
- **Size:** letters about 80 px tall including the outline (font size 92, Inter Display ExtraBold); scaled down if a caption would be wider than 600 px.
- **Rendering:** flat fill, a thick black outline (~0.17 of the font size), and a soft dark drop shadow 8 px lower.
- **Grouping:** **1-2 words per caption**, always breaking at punctuation. A caption appears on its first word with a pop (0.85 → 1.0, small overshoot) and stays until the next one; it is hidden during pauses longer than 0.6 s.
- **Key words** are in CAPITALS (numbers, nouns that carry the joke, shouted words, the last word of a punchline), and the whole group takes one colour, e.g. "your MOM" is all pink.

  | Colour | Hex | Used for |
  |---|---|---|
  | yellow | `#fccc0c` | chapter / time markers, numbers, rewards |
  | green | `#3ce454` | success, game words |
  | red | `#ff3b3b` | danger, "no", failures |
  | pink | `#fc6ccc` | mom / family / cute |
  | purple | `#cc84fc` | pleading, weird |
  | orange | `#fcb40c` | food, gold |
  | blue | `#54ccfc` | calm, tech, water |

- **All other words** are white in normal case ("What if", "seconds.", "Then you").
- **No duplicates** (the user's rule): if the same text is already on screen at that moment (a scene label, chapter card, speech bubble, HUD or UI text), it is left out of the caption. `assembler/captions.py ... animator/<story>.py` does this automatically.

## 2. Look in one line
A flat **2D vector cartoon of blocky game avatars**: rounded-rectangle head, torso, arms and legs, with a thick outline in a dark shade of each part's own colour.
- Large expressive faces in an anime/cartoon style, with soft gradient shading and glossy highlight streaks.
- Very saturated colours.
- Every place is either a real room (a dark-navy night bedroom, a sunny living room) or a bright game world with game UI on top.

## 3. Characters (all sizes in head-widths, hw)
Measured on full-body frames: kid at 0:25.6 in momplays, kid at 0:12.6 in tensec, the noob at 0:09.8. They were cross-checked on close-ups.

| Part | Size | Notes |
|---|---|---|
| Head (face block) | **1.0 hw wide x 0.9 hw tall**, corner radius 0.18 hw | Slightly wider than tall. The face fills it |
| Hair / headwear | adds ~0.3 hw on top, 0.1 hw on each side | A cap-like shape over the head |
| Neck | none | The head sits right on the torso; the head casts a soft shadow band on the torso top |
| Torso | **1.1 hw wide x 1.05 hw tall**, radius 0.08 hw | Slightly wider than the head |
| Arms | **0.55 hw wide x 1.15 hw long**, radius 0.1 hw | Rigid blocks that pivot at the shoulder; no elbows. Hands are the last ~35% of the arm in skin colour when sleeves are short (mom's robe, noob); a long-sleeve shirt colours the whole arm (kid) |
| Legs | **0.55 hw wide x 1.0 hw tall** each | Two blocks side by side, as wide as the torso together. A thin dark line splits them |
| Feet | none (blocks end flat) | Optional white shoe band 0.13 hw tall (kid) or **bunny slippers** (mom) |
| Total height | **~3.25 hw** with hair (2.95 hw without) | Head ≈ 28% of the height (chunky, not chibi) |
| Height ratios | Everyone is the same height | Grandma is the same block body. Crowds use the same model at a smaller scale |
| Outline | **colour = the fill darkened ~70%** toward a deep brown-purple (`#2a1e2e`), never pure black | Width ≈ **0.028 hw** in full body (4 px at hw 150) and 0.018 hw in close-ups (7 px at hw 385). In code: `max(2, 0.026 hw)` |
| Light | Key from the **top-left** | Every block has: a lighter top band, a darker bottom, and a soft **inner glossy highlight** (thin white streak inside the top-left edge, ~35% opacity) |
| Shading | Soft vertical gradient (+12% light at the top, -12% at the bottom) | A darker shadow band under the head on the torso, and a darker inner line between the legs |
| Rim light | In night scenes, a warm rim (`#ffd27a`, ~30%) on the side facing the door or lamp | Plus a soft glow behind the figure in the doorway |
| Shadow | Soft dark ellipse under the feet (0.9 hw wide) | |

`animator/style.py` measures `Block.HW = 1.45 r` (r = 64·s px), so a character at `s=1` is about 300 px tall, the same as the old `Char2`. Stories can swap between them.

### Cast used in the references (types only; we design our own people)
| Type | Look |
|---|---|
| Kid ("you") | Pale cream-grey face `#e6ddd6`, brown bowl hair `#8d5e3b` with lighter wavy lines and a jagged fringe, red-orange long-sleeve shirt `#e8573a` with a white lightning-bolt emblem, red pants, white shoe band. In the game he wears a red/white headband |
| Mom | Tan skin `#c89f82`, brown bun with **pink curlers** and side curls, lavender robe `#a694e1` with lapels, white undershirt, pearl necklace, belt, pink bunny slippers. Lashes (3 strokes) on each eye |
| Noob | Yellow skin `#e9c22c`, blue torso `#1a68cf`, green legs `#9bbc36` |
| Crowd | Same block model in bright shirts: pink, purple, yellow, blue, with caps and long hair. Faces vary in skin (cream, tan, dark brown) |
| Grandma | Grey bun, round glasses, pink gamer headset, pink cardigan |
| Boss | A giant noob with a gold crown, an angry face and a red health bar |

### Our own cast (`animator/style.py`)
Same style, our own designs; none of them copy the reference channel's people.

| Name | Look |
|---|---|
| `KID` | "you": teal shirt with a yellow star, navy pants, white shoes, dark-brown bowl hair |
| `KID_GAME` | the kid's avatar in the game, plus a red/white headband |
| `MOM` | coral cardigan, auburn ponytail, tan skin, lashes |
| `MOM_ROBE` | blue robe, bun with yellow curlers, bunny slippers |
| `DAD` | blue suit, red tie |
| `GRANDMA` | lilac cardigan, grey bun, glasses |
| `NOOB` / `BOSS` | the generic yellow/blue/green default avatar; the boss adds a crown |
| `crowd_member(i)` | varied bystanders |

New looks are one line: `Block(shirt, pants=, skin=, hair=, hair_col=, outfit=, emblem=, shoes=, headband=, headset=, glasses=, crown=, cap=, lashes=, curlers=, shades=)`.

## 4. Faces and the expression set
**Placement:** eyes at 52% of the head height and 0.22 hw from the centre line. Mouth at 76%. Brows at 33%, as thick dark rounded bars (0.2 hw long, 0.05 hw thick). Pink blush ovals under the eyes in happy moods.

**Default eyes:** tall black ovals (0.11 x 0.15 hw) with a white highlight dot at the top-right. Pupils move with `look`.

| expr | Eyes | Brows | Mouth | Extras | Seen on |
|---|---|---|---|---|---|
| neutral | ovals | flat | small curve | | listening |
| happy | **^ ^ closed arcs** | raised | open D smile, pink tongue | blush | crowd, toaster |
| grin | ovals | raised | wide toothy smile (white teeth band) | blush | "Gimme!" |
| laugh | closed arcs | raised | huge open mouth, tongue | tears of joy | |
| smirk | **half-lid** (flat top line over the eye) | one raised, one flat | sideways smile | | mom "seconds." |
| smug | half-lid, eyes to the side | angled down to the centre | smile with **tongue out** | | kid "SPEEDRUNNER." |
| cold | half-lid | flat, low | flat line | | mom "go to bed" |
| shock | **white circles, tiny pupils** | high | tall O mouth | face goes **pale blue**, sweat drops, shake lines | kid "TEN SECONDS?" |
| scared | white circles, tiny pupils | worried | **wavy zig-zag** mouth | pale blue face, sweat | kid "three..." |
| angry | ovals with **red rims** | V shape | open shouting mouth, top teeth | **red anger mark**, face reddens | mom "JUMP?!" |
| cry | ovals | inner ends up | open wail | **blue tear streams** down the cheeks | kid "my Robux?!" |
| sad / worried | ovals, smaller | inner ends up | small frown | | |
| crazy | white eyes with red veins | high | giant toothy grin | | mom "PLAYING ROBLOX?" |
| wink | one ^ and one oval | raised | open smile | | mom "BLOCKY" |
| stars | **yellow stars** | raised | open smile | sparkles | crowd "SUBSCRIBES" |
| sleepy | closed lines | low | small o | | mom asleep |
| determined | ovals | V | flat line | | |
| forced | ovals | worried | toothy grin | sweat | |

Expressions **snap on the key word** (every 0.5-1.5 s in close-ups). A close-up face (head 50-80% of the frame width) appears about every 4-6 s.

## 5. Palette (hex, measured)
| Use | Colours |
|---|---|
| Night bedroom | wall `#272b6d`, wall top `#25286a`, window sky `#0f1447`, moon `#f6e7a8`, curtain teal `#2b9a9a`, rug `#1d8381`, floor `#3e2e3e`, door light `#f2c46a`, lamp `#f2daa2` |
| Bed blanket | checker orange `#e58747` and teal `#339891` |
| Day room | wall cream `#f6e2b4`, window sky `#8fd3ff`, curtain teal `#2b9a9a`, blanket blue `#2f5bd3` with white stars |
| Game sky | top `#84d4fb`, horizon `#b8e8fb`, block clouds `#fdffff` |
| Baseplate | grass `#51c844` with lighter studs `#7fe06f` |
| Obby | lava `#fa801a` / `#fcab17`, platforms cyan `#2cd5fc`, pink `#fa3a9f`, yellow `#f7e04a`, purple `#a694e1` |
| Boss arena | sky pink-magenta `#c2367f`, castle purple `#6b3fa0`, floor tiles `#8d6bd6`, torches orange |
| Throne / reward | purple `#7a3fb8`, gold `#ffcc33`, red carpet `#d8283a` |
| UI | timer pill `#1e2230` (urgent `#e8323a`), cards white with a dark outline, green `#4fd16a`, blue `#2f6bd8`, gold `#ffcc33` |
| Text colours | white, yellow `#ffd84a`, green `#4fd16a`, red `#ff4f5a`, pink `#ff5fb0`, all with a dark outline |
| Skin | kid `#e6ddd6`, mom `#c89f82`, noob `#e9c22c`, dark `#7a4a2e` |

Measured shot brightness median **0.43-0.51**, saturation **0.46-0.53**. Night scenes are 0.25-0.35; game scenes 0.6-0.7.

## 6. Sets and backgrounds
| Set | Contents | Mood |
|---|---|---|
| Night bedroom (home base) | Navy wall with tiny 4-point stars and a green dino poster. Window with crescent moon and night skyline. Teal curtains, bed with wood headboard and checker blanket, nightstand with **red alarm clock showing the timer**, lamp with warm cone, teal oval rug, door with a warm light spill | Tension/rules: cool navy + one warm door or lamp light |
| Gamer desk | Same room from the front: monitor glow on the face, energy cans, snack bag, RGB headset, digital clock "3:00" | Late night |
| Day room | Cream wall, sunny window, teal curtains, blue star blanket | Normal / everyday |
| Game spawn | Sky, block clouds, studded grass baseplate, round spawn pad, grey brick wall, joystick + JUMP button UI, chat/menu buttons, "joined the game" toast | Game start |
| Obby | Coloured floating blocks over orange lava, stage numbers on blocks, "STAGE 97" pill, checkered finish flag, confetti | Action |
| Boss arena | Purple castle wall, pink sky, torches, tiled floor with a gold rune circle, boss health bar | Danger |
| Leaderboard / shop / comments | Full-screen game UI panels: rows, gold #1 badge, OWNED stamps, BUY buttons, phone keyboard | Explanations, lists |
| Burst backgrounds | Radial rays: gold (reward), red (alarm), purple (legendary), blue (calm), dark with a gold glow (secret item) | Reveals |
| Throne room | Gold throne, purple banners, red carpet, crowd in front | Victory |

**Depth of field:** almost none. The style is flat vector. Only foreground props (a blurred shoulder, a tablet edge) are softened, and only in close-ups (`dof=1-2`).

**Lighting by mood:**
- Normal: bright day colours.
- Night or rules: navy + warm door/lamp spill.
- Danger: red tint + dark vignette.
- Reward: gold rays + sparkles.
- Shock: the face turns pale blue + shake lines.
- Secret item: dark with a golden glow.

## 7. Recurring graphics (the "game layer")
These are drawn in `animator/sets.py`:
- Timer pill: dark, red when 4 or less.
- "SECOND N" card with a shockwave ring.
- "DAY N" hand-painted yellow text with an underline swoosh.
- Floating damage numbers and a CRITICAL HIT banner.
- "K.O.!" sticker.
- Health bar.
- Stage pill.
- Leaderboard, shop grid, gamepass card, comments sheet with keyboard.
- Robux-style coin pile and counter.
- Egg and pet with a rarity banner.
- Notification toast.

**Reaction FX** (`animator/sets.py`): sweat drop, anger mark, tears, shake lines, speed lines, impact star "BONK!", sparkles, confetti, hearts, poof cloud, shockwave ring.

## 8. STYLE LOCK (one paragraph to paste into any prompt)
> Flat 2D vector cartoon of blocky game avatars: rounded-rectangle head (1.0 x 0.9), torso (1.1 x 1.05), block arms and legs (0.55 wide), no neck, no hands or feet beyond the blocks. Thick outlines in a dark shade of each colour. Soft top-left light with glossy white highlight streaks. Big expressive cartoon faces (black oval eyes with a white highlight, thick rounded brows, D-shaped open mouths with pink tongues). Very saturated colours: navy night bedroom with a warm door light, bright sky-blue game worlds with studded green baseplates, orange lava obbies, purple boss castles, gold reward bursts. Game UI overlays: timer pill, stage pills, health bars, leaderboards. Hard cuts, a punch-in zoom on every key word, screen shake on impacts.
