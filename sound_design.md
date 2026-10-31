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

## 3. Defaults for every new video (animator)
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
