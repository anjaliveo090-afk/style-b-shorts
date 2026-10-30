# Visual grammar: how Style B turns each phrase into a picture

Measured on the 2 references (`analysis/ref_data/`). Tools:
- `new_visuals.py`: how often the picture changes.
- `flow.py`: camera speed.
- `shots.py`: camera move per shot.
- `frame_log.py`: 4 fps contact sheets with the spoken line.

This is a rulebook. Tag every phrase of a new voiceover with a row from section 2 before building shots.

## 1. Measured pace and camera
| What | tensec | momplays | **Target for our renders** |
|---|---|---|---|
| New visual every (`new_visuals.py`) | 1.43 s (median gap 1.10 s, 90% under 2.68 s) | 1.18 s (median 1.00 s, 90% under 1.50 s) | **1.1-1.6 s**, never a gap over ~2.7 s |
| Camera speed median / mean (`flow.py`, % width/s) | 2.1 / 6.4 | 4.5 / 10.5 | **median 2-5, mean 6-11** |
| Non-camera motion (`flow.py`) | 5.9 | 7.3 | **5-8** (characters and props move more than the camera) |
| Shot length median (`shots.py`, splits on cuts and big pops) | 0.8 s | 0.6 s | 0.6-1.2 s |
| Static hold | 48% | 28% | camera mostly still... |
| Slow drift | 21% | 44% | ...or drifting slightly |
| Push-in | 19% (median x1.15) | 10% (x1.19) | short **punch-in** x1.12-1.25 landing on the key word |
| Pull-out | 10% (x0.92) | 14% (x0.87) | short pull-back to reveal |
| Pans | 2% | 4% | rare: a whip pan as a transition |
| Brightness / saturation (median) | 0.51 / 0.46 | 0.43 / 0.53 | 0.4-0.55 / 0.45-0.55 |

How this compares with the old channel in `reference_examples/`:
- **Much faster picture changes**: 1.2-1.4 s against 1.5-2.6 s.
- **A calmer camera**: median 2-5 against 4-15.
- **Hard cuts instead of dissolves.**

The energy comes from the cuts, the pops and the faces, not from camera travel.

## 2. Phrase type → what is shown → camera → character reaction
| # | When the phrase... | Show | Camera | Character | Example in the references |
|---|---|---|---|---|---|
| 1 | Hook question "What if your mom..." | The main place with **both characters**: kid in front, mom in the doorway or at a desk. Timer/HUD already visible | Slight push; the expression snaps on "mom" | Kid shocked (pale, shake lines), mom smirk | tensec 0:00: night bedroom, kid in bed with a laptop, mom in the door; momplays 0:00: mom close-up in a gamer headset |
| 2 | A rule / an order ("10 seconds, then you go to bed") | **Close-up of the speaker holding the object** (alarm clock 0:10) | Medium close-up, punch-in on the number word | Smirk → cold on "bed", arm points | mom in the door holding the clock |
| 3 | Disbelief ("10 seconds?") | **Face close-up**, head 60-80% of the width | Punch-in x1.2 + shake | shock: white circle eyes, pale blue face, sweat, shake lines | kid "TEN SECONDS?" |
| 4 | A cool turn ("unless you're a speedrunner") | **Extreme close-up**, face fills the frame, dutch tilt | Quick push to the eyes | smug (half-lid + tongue), sparkle on the eye | kid "SPEEDRUNNER." |
| 5 | Countdown / chapter marker ("Second 10", "Day 2") | A **big card or painted text** pops over the new place: "SECOND 10" card with a shockwave ring, or "DAY 2" brush text with a swoosh | Hold; the card flies in | Character small, below | every chapter |
| 6 | Entering the game | **Dive into the screen**: zoom through the monitor or phone into the game world, or a spawn beam | Fast zoom-through (0.3 s) | Avatar spawns in a light beam | momplays "She spawns as a noob" |
| 7 | Names a game thing (obby, boss, shop, pet) | **That exact thing**, big, with its UI: stage pill, boss health bar, shop grid, egg + rarity banner | Wide establishing, then punch-in | Avatar reacts small | "100-stage obby", "Noob King spawns" |
| 8 | A number or amount ("a billion Robux", "100 stages") | A **counter that rolls** on screen (stage 3/100 → 75/100, 92,676 → 999,999,999) plus a physical pile | Static; the pile grows | Avatar buried, happy | Robux pile |
| 9 | An action verb (punch, jump, beat, buy, hatch) | The action **literally**, in 1-3 quick cuts: wind-up, hit with an impact star, result | Shake on the hit | angry/determined → happy | "One punch, KO!" → POW + K.O. sticker |
| 10 | A list / "every" ("every game pass", "every leaderboard") | **A grid of items getting stamped** one by one (OWNED ✓), or several boards side by side | Slight drift or pull-out | Small reactions per item | shop grid, leaderboards |
| 11 | A silly twist ("turns you into a toaster") | The **transformation**: poof cloud, then the result with the same face | Punch-in on the result | Result looks smug at the camera | toaster with the kid's hair |
| 12 | A call to action ("everyone who subscribes") | **The UI element** itself (SUBSCRIBE button → SUBSCRIBED, a finger presses it) plus a crowd cheering with **star eyes** | Static | Crowd in sync | "SUBSCRIBES" |
| 13 | Time almost up ("4... 3...") | Timer turns **red**. Alternating **face close-ups** of mom (angry, red light) and kid (scared, blue) | Punch-in + red vignette | angry vs scared | "FOUR...", "THREE..." |
| 14 | A discovery ("then you find... this!") | The object in a **dark scene with a golden glow** and gold rays, held up to the camera | Push-in, then hold | Star eyes peeking from the side | the "+10 SECONDS" gamepass card |
| 15 | Slow motion / a dramatic beat | **Freeze and slow the action** (a figure mid-air), speed streaks, darker | Very slow drift | Exaggerated mid-air poses | "Mom dives. Everything goes slow-mo." |
| 16 | A reveal of a person ("and then grandma logged in") | **Silhouette in the dark with lightning**, then a burst to the full colour reveal | Hold, then punch-in | Big confident grin | grandma reveal |
| 17 | A quote from mom/kid ("Did you spend my Robux?") | **Speaker close-up**; the face changes 2-3 times inside the line | Punch-in on the loudest word | angry → cry | kid "MY ROBUX?!" |
| 18 | A gaming habit in real life ("while folding laundry") | **Split real life + game**: mom folding laundry with the tablet beside her | Medium | Calm smirk = mastery | laundry + tablet |
| 19 | Call to comment ("Comment loop if...") | A **phone comments sheet** with a keyboard; the word is typed, likes fly up | Static | none | both endings |
| 20 | Loop ending | A **REWIND** scrub (whip-blur or a rewind icon) back to the first frame | Whip pan | Same as shot 1 | tensec 49.5 s |

## 3. Composition
- Safe zone: the whole character and key props inside x 38-680, y 149-1013 (below y 678 only to x 599). Run `safezone.fit(SHOTS, module)` before render. Use `keep=[...]` for key props and `top=250` under the HUD.
- **Face close-ups** (rows 3, 4, 13, 17) are the exception: the body runs off the bottom of the frame. Mark the shot `closeup=True` and add the face box to `keep=[...]`. safezone then keeps the face and labels in the zone and ignores the body (see `sample.py` `FACE_KEEP`).
- **Characters are big.** A full body fills 40-60% of the frame height; close-ups crop at the chest or tighter. Wide shots are rare (crowds, arenas) and short.
- The main subject is centred or slightly off-centre. A second character is at the frame edge, often cut off (a shoulder or half a head) for depth.
- Labels and cards sit in the upper third, under the HUD. Characters sit in the middle third.
- Dutch tilt (±0.05-0.1 rad) on smug and cool beats.

## 4. Performance
- Expressions snap on the key word, often 2-3 changes in one sentence.
- Bodies: blocky limbs swing in big, readable poses (arms up, arm thrust forward, crossed arms, a leaning point). There is a constant small bounce/idle sway; nothing is ever fully still.
- Squash on landing; jump arcs; impacts get a 2-frame white flash and a shake.
- **No lip-sync** in the references: mouths change shape by expression, not phoneme by phoneme. Our default is `engine.LIPSYNC = False`.

## 5. Transitions
- **Hard cuts** for almost every change. These fall on the word (on the first syllable of the phrase the new picture illustrates).
- Card pops (scale overshoot 0.2 s) inside a shot count as new visuals.
- A **whip pan** with motion blur when changing world (real life ↔ game), about once per video.
- A **zoom through a screen** (monitor or phone) to enter the game.
- No cross-dissolves: `render(..., xfade=0)`.

## 6. Rhythm of a ~50 s video
1. 0-3 s: hook question. Both characters in the home set, HUD visible.
2. 3-10 s: the rule (mom close-up), the reaction (kid close-up), the twist (smug close-up).
3. 10-30 s: chapters ("Second N" / "Day N"). Each chapter is 3-5 s and 3-4 visuals: chapter card → thing named → action → result.
4. 30-45 s: escalation. Countdown in red, the secret item, slow motion, the confrontation.
5. 45-50 s: comment call (comments UI), then a loop back to the first frame.

## 7. Applying it to a new voiceover
1. Get word times (`analysis/align_words.py`).
2. Split the narration into phrases of 2-4 words. Give each phrase a row from section 2.
3. One visual per phrase. Cut on the phrase's first word, then punch-in or pop on the key word.
4. Put expression snaps and card pops on key words, and one SFX on every pop, hit or snap (see `sound_design.md`).
5. Check: `new_visuals.py` (1.1-1.6 s), `flow.py` (camera median 2-5, mean 6-11).

## 8. Measured on our sample (`animator/sample.py`, 22 s)
| Measure | Sample | Target |
|---|---|---|
| New visual every | 1.31 s (median gap 1.10 s, 90% under 2.04 s) | 1.1-1.6 s |
| Camera median / mean | 3.3 / 11.4 | 2-5 / 6-11 |
| Non-camera motion | 5.5 | 5-8 |

How it was achieved:
- 22 shots, a hard cut on every phrase (`render(xfade=0)`);
- punch-in keys of 0.1-0.2 s on key words;
- `engine.DRIFT = (0.02, 5, -3)` (a calm hold);
- `engine.ENERGY = 3.0` (lively idle bounce).

The camera mean sits slightly above the target because of the punch-ins and the rewind whip. Use fewer or smaller punches if a render reads above ~12.
