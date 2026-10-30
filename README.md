# Style B Shorts: blocky game animation toolkit

Turns **any voiceover + SRT** into a 9:16 animated Short in one fixed visual style. The style was measured frame by frame and sound by sound from the user's reference videos ("what if your mom… Roblox" type Shorts).

**The look:** flat-vector blocky game avatars with big expressive faces, a navy night bedroom and bright game worlds (obbies over lava, boss arenas, leaderboards, shops), game UI overlays, hard cuts, punch-ins on key words, loud punchy SFX over a cheeky G-centred game tune.

Everything is drawn and synthesised in code (pycairo + numpy + ffmpeg). Only the style is copied, never the reference channel's characters, logos, text or sound files.

## Make a video (new chat)
Open a new Claude Code chat on this repo, attach your voiceover and its SRT, and send:

```
I am attaching a voiceover and its SRT. Run bash setup.sh, then read MASTER_PROMPT.md and follow the prompt inside it exactly.
```

## What is in here
| Path | What |
|---|---|
| `CLAUDE.md` | The workflow Claude follows for every voice + SRT |
| `MASTER_PROMPT.md` | The full prompt (voice + SRT → video), defaults and measured targets |
| `style_bible.md` | The look: proportions in head-widths, faces and expressions, palette, sets |
| `visual_grammar.md` | Measured pace and camera, and the phrase type → shot → reaction table |
| `sound_design.md` | Measured music and SFX, mix defaults and check targets |
| `animator/style.py` | `Block` characters (19 expressions, 12 arm poses, 6 leg poses) and our own cast |
| `animator/sets.py` | Rooms, game worlds, props, game UI, FX |
| `animator/sample.py` | Template story (22 s sample) |
| `animator/report_noob.py` | Full 60 s story on a real voiceover ("This noob is the reason Roblox invented the report button") |
| `animator/contact.py` | Contact sheet of a story with the safe zone drawn, before rendering |
| `animator/test_sheet.py`, `animator/set_sheet.py` | Style test sheets (characters × expressions × poses, all sets) |
| `animator/engine.py`, `audio.py`, `safezone.py`, `thumbnail.py` | Render engine, synthesised sound + music, safe-zone fitter, thumbnail template |
| `assembler/` | Joins animation + voice + music + SFX into the final mp4; `captions.py` burns reference-style captions onto it |
| `animator/no_break.py` | Full 60 s story on a real voiceover ("How long could you survive playing Roblox without a break?"), with a playtime HUD; captions in `animator/captions/no_break.json` |
| `analysis/` | Reference analysis tools (frame logs, SFX/music measure, pace, camera flow, word alignment) and `ref_data/` |
| `reference_examples/` | The older toolkit (another style) this repo was bootstrapped from, kept as worked examples |

## Quick test
```bash
bash setup.sh
```
```bash
python3 animator/audio.py output/sample/sfx 22.3
```
```bash
cd animator && python3 sample.py ../output/sample/clips/animation.mp4 ../output/sample/cues.json && cd ..
```
```bash
python3 assembler/assemble.py --clips output/sample/clips --voice <a 22 s voice file> \
  --sfx output/sample/cues.json --sfx-dir output/sample/sfx --music output/sample/music.wav \
  --music-volume 0.5 --out output/sample/sample_final.mp4
```
