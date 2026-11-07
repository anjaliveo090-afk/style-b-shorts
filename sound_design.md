# Sound design: Style B (measured on the 2 references)

`analysis/audio_ref.py` splits each soundtrack into voice and music+SFX with the UVR MDX-Net model, then measures:
- every SFX: time, kind, loudness against the voice;
- the music: level, key, tempo, drums, density.

The raw data, including every SFX with its time and the line spoken, is in `analysis/ref_data/tensec.json` and `momplays.json`. Loudness is RMS in dB relative to the narration (0 dB = as loud as the voice).

**This style is much louder and busier than the old channel in `reference_examples/sound_design.md`.** Do not reuse those targets.

## 1. Music
| What | tensec | momplays | Rule for our videos |
|---|---|---|---|
| Level vs voice | **-10.5 dB** (x0.30) | **-10.0 dB** (x0.31) | Music about **-10 dB** under the voice: clearly audible, playful |
| Key (whole track) | G minor (fit 0.62) | G major (fit 0.53) | **Centred on G** with chromatic neighbours (G, F#, F, G#, E are the strongest chroma). It reads as a cheeky "sneaky/bouncy" game tune that swings between major and minor, not a sad minor bed |
| Tempo | 120 (segments 91-136) | 136 (segments 82-152) | About **120 bpm** with eighth-note ticks |
| Drums | percussive share 0.14 (0.11-0.16) | 0.22 (0.14-0.34) | **Light percussion**: soft ticks/hats on eighths, a soft kick every bar. No heavy beat |
| Density | 2.3 notes/s | 1.6 notes/s | About **2 notes/s**, staccato |
| Tone | bass 53%, mid 30%, high 17% (centroid 1460 Hz) | bass 51%, mid 27%, high 22% (1680 Hz) | Bouncy bass + bright plucky lead (square/marimba-like) |
| Shape | almost **silent for the first ~5 s** (-50 dB), comes in under "That's nothing" and dips under the slow-motion beat | constant, with dips under quiet beats | Start the bed under the hook or after it, at full level by ~3-5 s. Dip it 6-10 dB under a dramatic/slow-motion beat, and end on a short stinger |

Our generator: `animator/audio.py music_game(total, start=..., dips=[(t0, t1), ...])`. It plays a G | Gm | Eb | D7 swing with a soft root-fifth bass and a marimba + square lead at 120 bpm. All attacks are 8 ms or longer and there are no noise hats, so the analyser does not mistake the music for SFX. It is checked with `audio_ref.py` (section 4).

## 2. SFX
| What | tensec | momplays | Rule |
|---|---|---|---|
| How many | **11.0 per 10 s** (55) | **11.8 per 10 s** (60) | **About 1.1 per second**: one per pop, hit, card, counter or face snap |
| Loudness (median vs voice) | **-2.7 dB** | **-3.5 dB** | SFX are **almost as loud as the voice**. Hits and stings reach +4 to +9 dB |
| Length | median ~0.1 s | ~0.1 s | Short and punchy; stings 0.3-0.9 s |
| On a visual change | 55% (random 34%) | 62% (random 49%) | SFX land **on** visual events: the cut, the pop or the hit |
| On detected cuts (`audio_ref` "on cuts") | 65% | 78% | High, because hard cuts and card pops coincide with SFX |

**Mix by kind** (115 SFX):

| Kind | Share | Typical level | Used for | Our file |
|---|---|---|---|---|
| pop / snap / swish | 38% | -5 dB | card and label pops, an expression snap, an arm swing, the poof cloud | `pop.wav`, `boing.wav`, `swish.wav` |
| tick / click | 25% | -6 dB | counters rolling, UI taps (BUY, SUBSCRIBE), typing, timer ticks | `tick.wav`, `click.wav` |
| thud / boom | 22% | +3 dB (the loudest) | countdown numbers ("FOUR...", "THREE..."), punches, landings, "SECOND N" cards, slams | `thud.wav`, `boom.wav` |
| ding / chime / sting | 12% | +2 dB | reveals (egg, gamepass, legendary), "KA-CHING", the comment-loop line | `ding.wav`, `sparkle.wav`, `coin.wav`, `chaching.wav` |
| whoosh | 3% | -2 dB | **only** the whip-pan/rewind loop transition and a thrown object | `whoosh.wav` |

### What triggers SFX (from the frame at every SFX, `audio_ref` `_sfx.png`)
| Trigger | SFX |
|---|---|
| Hook word ("mom") | thud |
| "SECOND N" / "DAY N" card | thud or ding + whoosh-y pop |
| Expression snap | pop |
| Punch or hit | thud + pop, then a tick on the damage number |
| Counter rolling | a stream of ticks (4-5 per second) |
| Shop / subscribe tap | click + pop |
| Reveal | ding / sting, often the loudest SFX of the section |
| Countdown in red | a big thud per number |
| Comment line | ding |
| Loop rewind | whoosh |

## 2b. All 7 references side by side (set 3 added 2026-11-04)
Measured with `audio_ref.py` on the downloaded references. dB are relative to the narration.

| Reference | Music vs voice | SFX per 10 s | SFX median vs voice | SFX on cuts | Music key / bpm | Percussive share |
|---|---|---|---|---|---|---|
| tensec | -10.5 | 11.0 | -2.7 | 65 % | G minor / 120 | 0.14 |
| momplays | -10.0 | 11.8 | -3.5 | 78 % | G major / 136 | 0.22 |
| blink | -12.3 | 12.5 | -5.1 | 87 % | F# minor / 123 | 0.13 |
| dad noob king | -15.2 | 10.4 | -8.2 | 91 % | G major / 140 | 0.20 |
| hacked | -13.5 | 11.3 | -6.7 | 81 % | D major / 94 | 0.26 |
| **never_stop** (set 3) | **-20.2** | 12.5 | **-11.4** | 85 % | D major / 133 | 0.20 |
| **bff_quit** (set 3) | **-14.9** | 10.2 | **-8.4** | 79 % | G minor / 126 | 0.22 |
| **median of 7** | **-13.5** | 11.3 | **-6.7** | 81 % | G / D, ~126 | 0.20 |

What set 3 changes:
- **The newer videos are mixed quieter under the voice.** Music sits around -15 dB (never_stop -20) and SFX around -8 to -11 dB. The new targets below use the median of all 7.
- **Fewer booms.** Set 3 SFX kinds: pops 45-55 %, ticks/clicks 15-33 %, dings/chimes 16-21 %, thuds/booms only 5-7 % (3-5 per video), whoosh 1-2. Booms are kept for the 3-5 biggest moments (the DAY 5 power cut, a slam); the comic sound-word stickers (`sfx_word`) get a pop or a tick.
- 79-85 % of SFX land on a cut.
- Keys: G or D (D is G's dominant), 126-133 bpm. The bed stays "G-centred".

## 3. Defaults for every new video (animator)
**With `engine.profile("set3")` (the default for new stories since 2026-11-04):**
- Music: `MUSIC = dict(bpm=128, perc=0.6, dips=[...])`, mixed with **`--music-volume 0.45`** (about -14 dB under a voiceflow voice).
  - `perc` adds a soft kick and a woodblock. `audio_ref.py` counts part of them as SFX (perc=1 alone read 3.7 per 10 s at -6.6 dB) and still reports a low percussive share; the references' numbers include the same effect. Keep perc at 0.6 and count it in the SFX budget.
- SFX: **`SFX_GAIN = 0.2`** for the user's voiceflow voice (0.28 measured -3.6 dB; set 3 wants about -7). About 1.0-1.1 SFX per second in the `SFX` list (the music adds a few counted ones).
- Kind mix: ~50 % pop (every `sfx_word` sticker, card and label pop), ~25 % tick/click/type, ~15 % ding/sparkle/success, **3-5 booms in the whole video**, `whip.wav` only on the rewind and `swish` on a whip pan.
- Targets (section 4 table): music **-13.5 ± 3 dB**, SFX **10-12.5 per 10 s**, SFX median **-4 to -9 dB**, key G (or D).

**Older stories (30 fps, no profile)** keep the numbers below, so their fix renders still match.

These were calibrated by measuring assembled mp4s with `audio_ref.py` (section 4):
- `animator/report_noob.py`: a real recorded voiceover, 60 s. **Use these numbers.**
- `animator/sample.py`: a TTS test voice.

1. **Music:** `audio.music_game(TOTAL, **MUSIC)`. The story's `__main__` writes it as `music.wav` next to `cues.json`. Mix it with **`--music-volume 0.5`**: that measures **-10.1 dB** under a real voiceover (the quieter TTS sample needed 0.4). One track for the whole video.
   - For a hook without music, use `MUSIC = dict(start=3.0)`.
   - For slow-motion or dramatic beats, use `MUSIC = dict(dips=[(t0, t1), ...])` (about 9 dB quieter).
2. **SFX:** about 1.1 per second, in the story's `SFX` list (time, file, volume), written to `cues.json` with **`SFX_GAIN = 0.4`** for a real recorded voice (every volume × 0.4).
   - The TTS sample needed only 0.17. Real speech makes the separation step pull part of each SFX into the voice stem, so the same mix measures ~9 dB quieter.
   - **Always measure, then adjust `SFX_GAIN`** until the median sits around -3 dB. Only `cues.json` changes, so no re-render is needed.
   - Kind mix: about 40% pop, 25% tick/click, 20-30% hit, 10% ding.
   - No whoosh except the loop rewind (`whip.wav`).
   - Script volumes before the gain:

     | Kind | Files | Volume |
     |---|---|---|
     | pops / swishes | `pop`, `swish`, `boing` | 0.6-0.8 |
     | ticks / typing / clicks | `tick`, `type_key`, `click` | 0.5-0.8 |
     | hits (the loudest, as in the references) | `hit` | **1.3** |
     | big slams | `boom` | **1.6** |
     | dings / reveals | `ding`, `sparkle`, `success`, `chaching` | 0.7-0.9 |
     | error | `buzz` | 0.8 |

   - With these settings `report_noob` measures 12.0 SFX per 10 s at a median of -2.8 dB vs the voice.
3. **Captions:** none by default. Do not pass `--srt` to `assemble.py`; any SRT turns captions on.
4. **Check** with `python3 analysis/audio_ref.py final.mp4 subs.srt /tmp/check`:

| Measure | Target | report_noob (real voice) | sample (TTS) |
|---|---|---|---|
| Music vs voice | **-10 ± 2.5 dB** | -10.1 dB | -10.4 dB |
| Music key | G (major or minor) | G minor (fit 0.77) | G minor (fit 0.78) |
| Music notes/s | 1.5-2.5 | 2.5 | 1.9 |
| SFX per 10 s | **9-13** | 12.0 | 9.0 |
| SFX median vs voice | **-1 to -7 dB** | -2.8 dB | -2.0 dB |
| SFX on a visual change | above the random share | 0.57 vs 0.49 | 0.65 vs 0.52 |
| Kind mix | ~40% pop, 25% tick, 20-30% thud, ~10% ding | 32% / 39% / 25% / 4% | 55% / 15% / 25% / 5% |

Known gap: the references' music has a percussive share of 0.14-0.22. `music_game` alone has about 0.07, because noise hats and kicks get counted as SFX by the analyser, so they were left out. In a full mix it reads 0.2, because SFX tails leak into the measure.

## 5. Situation score: the music follows the story (the user's rule, 2026-11-07)
"video me background music sab nahi diye ho situation ke hisaab se isko fix karo": one cheeky game tune under a whole
video (even with dips) is not enough. **The music changes with the situation**, with a hard music cut on the same beat
as the picture's cut. `animator/score.py` does it:
- The story defines `SCORE = [(t, mood), ...]` (the first at 0) and `STINGS = [(t, kind), ...]`. Its `__main__` writes
  `music.wav` with `score.music_score(TOTAL, SCORE, STINGS)`; to remake only the music:
  `cd animator && python3 score.py <story> ../output/<story>/music.wav`, then re-assemble (no re-render).
- Every mood is normalised to the steady level of `music_game` and offset by its `db`, so the same `--music-volume`
  (0.45 Shorts, 0.35 long) still works. Every mood stays centred on G (the key check still reads G), attacks >= 8 ms, no
  noise, never total silence (a stop is `drone`).
- `python3 score.py --demo <dir>` writes 8 s of every mood and sting to listen to.

| Situation | Mood | bpm | Sound | dB |
|---|---|---|---|---|
| Hook, CTAs, the loop rewind | `hype` | 136 | the game tune, busier riff, kick on every beat | 0 |
| Ordinary in-game fun, rules, shop | `game` | 128 | `music_game` itself | -1 |
| First sight of the new world | `wonder` | 108 | celesta arpeggios, soft pad (G D/F# Em C) | -1 |
| Night, bedroom, before the wish | `night` | 76 | music box over a pad (Gm Eb Cm D) | -4.5 |
| The wish / system message being applied | `magic` | 120 | climbing 16th celesta that swells | -1.5 |
| A joke scene (attendance, Dad, Mom, report card) | `comedy` | 116 | tuba oom-pah, pizzicato, staccato bassoon riff | -1 |
| Bored adults, a dull class | `awkward` | 70 | elevator e-piano maj7 chords, clock tick | -3.5 |
| A small fail or a sad line ("Still.", muted) | `sad` | 66 | slow pad + e-piano (Gm Eb Bb D) | -4 |
| The low point of the climax (health 1) | `low` | 60 | heartbeat under a dark pad | -4 |
| Running, sprinting | `chase` | 156 | driving bass, 16th square lead | 0 |
| The admin / principal / villain | `villain` | 96 | low "dun dun DUN" tuba march, timpani | -1.5 |
| Whispering, sneaking | `sneaky` | 100 | tiptoe pizzicato | -2.5 |
| Silly-spooky (zombie) | `spooky` | 108 | wobbly theremin over walking pizzicato | -1.5 |
| An embarrassing love moment (kiss emote) | `romance` | 84 (3/4) | cheesy waltz, violin | -1.5 |
| An announcement of the danger | `ominous` | 58 | low drone G/Ab, heartbeat, timpani | -3 |
| A clue, a note, a secret | `mystery` | 92 | celesta arpeggio, clock tick | -3 |
| The problem found / the plan | `tension` | 112 | low 16th ostinato G-Bb-Ab, rising | -2 |
| Training / studying montage | `montage` | 124 | determined G Bm C D, four on the floor | -0.5 |
| The cool pro character | `cool` | 96 | G dorian e-piano groove, finger snaps | -2 |
| The boss reveal | `boss` | 84 | heavy low brass, timpani, dark choir (Gm Ab) | +1 |
| The fight | `battle` / `countdown` | 150 | driving bass, brass stabs, toms (+ a ticking clock) | +0.5 |
| The comeback | `heroic` | 140 | brass melody G Eb F G | +0.5 |
| The last seconds of the fight | `final` | 164 | heroic + running celesta | +1 |
| The win | `triumph` | 128 | G C D G brass fanfare, marimba | +0.5 |
| Back to normal, the ending | `warm` | 92 | soft guitar arpeggio, pad | -2.5 |
| A one-beat stop ("Literally.", "Mostly.", lights out) | `drone` | – | a quiet G pad | -11 |

Stings (`STINGS`): `hit` / `hit_major` on a reveal or a big hit, `rise` (ENDS at its time) into a reveal, `drop`
(power-down) on a blackout or "let me explain", `fail` (sad trombone) on a fail, `fanfare` on a win or an entrance,
`sparkle` on a level-up or a magic moment. Skip a sting where a `boom` SFX already lands.

How many cues: a long video ~50 (one per situation, every 5-15 s; whole_school has 53 cues and 16 stings); a Short
3-6 (game → the twist → the win). Measured on whole_school: music -16.7 dB under the voice overall (long references
16-17 dB), -19/-20 dB under night/sad/awkward lines, -12/-15 dB under the boss/battle/final run; key G major (0.84);
2-15 notes/s and a centroid of 420-1410 Hz across the moods.
