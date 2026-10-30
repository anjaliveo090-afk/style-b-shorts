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

Our generator: `animator/audio.py music_game(total, start=..., dips=[(t0, t1), ...])`. It plays G major/minor with a chromatic walking bass, a staccato square/marimba lead, eighth-note hats and a soft kick, at 120 bpm. It is checked with `audio_ref.py` (section 4).

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

## 3. Defaults for every new video (animator)
These were calibrated on `animator/sample.py` by measuring the assembled mp4 with `audio_ref.py` (section 4).
1. **Music:** `audio.music_game(total)` (written as `music_game.wav` by `python3 animator/audio.py <sfx_dir> <total>`), mixed with **`--music-volume 0.4`**. That measures **-10.4 dB** under the voice. One track for the whole video.
   - For a hook without music, use `music_game(total, start=3.0)`.
   - For a slow-motion or dramatic beat, use `dips=[(t0, t1)]`.
2. **SFX:** about 1.1 per second, in the story's `SFX` list (time, file, volume), written to `cues.json` with **`SFX_GAIN = 0.17`** (every volume × 0.17).
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

   - With these settings the mix measures 9-11 SFX per 10 s at a median of about -2 dB vs the voice.
3. **Captions:** none by default. Do not pass `--srt` to `assemble.py`; any SRT turns captions on.
4. **Check** with `python3 analysis/audio_ref.py final.mp4 subs.srt /tmp/check`:

| Measure | Target | Sample (`animator/sample.py`) |
|---|---|---|
| Music vs voice | **-10 ± 2.5 dB** | -10.4 dB |
| Music key | G (major or minor) | G minor (fit 0.78) |
| Music notes/s | 1.5-2.5 | 1.9 |
| SFX per 10 s | **9-13** | 9.0 |
| SFX median vs voice | **-1 to -7 dB** | -2.0 dB |
| SFX on a visual change | above the random share | 0.65 vs 0.52 |
| Kind mix | ~40% pop, 25% tick, 20-30% thud, ~10% ding | 55% / 15% / 25% / 5% |

Known gap: the references' music has a percussive share of 0.14-0.22. `music_game` has about 0.07, because noise hats and kicks get counted as SFX by the analyser, so they were left out.
