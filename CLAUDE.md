# Project: Style B "blocky game" animated Shorts

This repo turns a voiceover + SRT into a 9:16 animated Short in one fixed style: flat-vector blocky game avatars, a navy night bedroom and bright game worlds, game UI, hard cuts, punch-ins on key words, loud punchy SFX over a cheeky G-centred game tune.

Everything is drawn in code: pycairo frames → ffmpeg. There is no AI video model.

When the user gives a voiceover + SRT (or a script), follow this workflow without being asked.

## Read first
| File | What it holds |
|---|---|
| `style_bible.md` | Look: format and safe zone, characters in head-widths, faces and the 19 expressions, palette, sets, STYLE LOCK |
| `visual_grammar.md` | Measured pace and camera; **section 2 = phrase type → what is shown → camera → reaction** (rows 1-20) |
| `sound_design.md` | Measured music and SFX, the mix defaults and the target numbers |
| `animator/sample.py` | **The template story.** Copy it for every new video |
| `animator/style.py` | Characters: `Block` (same `draw()` signature as the old `style2.Char2`), the cast `KID`, `KID_GAME`, `MOM`, `MOM_ROBE`, `DAD`, `GRANDMA`, `NOOB`, `BOSS`, `crowd_member(i)`, `back_figure`, and the FX `sweat`, `anger_mark`, `shake_lines`, `sparkle` |
| `animator/sets.py` | Places, props, game UI and FX (list at the top of the file) |
| `animator/audio.py` | Synthesised SFX + `music_game()` |
| `animator/engine.py` | Camera keys and render. Do not change unless broken |
| `animator/safezone.py` | Keeps characters, labels and `keep` boxes in the Shorts safe zone |

`reference_examples/` is the older toolkit this repo was built from (another style). Read it only for method; never import from it.

## Workflow for a new voice + SRT
1. **Words.** Strip any "(Transcribed by ...)" text from the SRT, then run
   `python3 analysis/align_words.py <voice> <subs.srt> output/<story>/words`.
   This gives a time for every word. Where pocketsphinx misplaces a word, trust the SRT line start.
2. **Plan the shots** with `visual_grammar.md`:
   - Split the narration into phrases of 2-4 words.
   - Give each phrase a row from section 2 (hook, rule, disbelief close-up, DAY/SECOND card, game thing, number counter, action, list, twist, comment call, loop...).
   - One literal visual per phrase, a **hard cut on the phrase's first word**, and a punch-in, pop or expression snap **on the key word**.
   - Aim for a new visual every 1.1-1.6 s, never more than ~2.7 s.
   - Write the plan as a table (time | words | row | what is shown | camera | expression | SFX) before coding.
3. **Build** `animator/<story>.py` by copying `animator/sample.py`:
   - Keep its helpers: `shot`, `punch`, `kid_face` / `FACE_*` close-ups, `SFX_GAIN`, `TOTAL`, the loop ending (`s_end` = first frame), and the `__main__` block.
   - Add new places or props to `animator/sets.py` in the same style: `style.block` / `shape_fill`, self-coloured outlines, palette from `style_bible.md` section 5. Never copy the reference channel's characters, logos or text.
   - Use our cast from `style.py`, or new `Block(...)` looks.
4. **Contact sheet with the safe zone** before the full render:
   `cd animator && python3 contact.py <story> ../output/<story>/contact.png 1`.
   Look at it and fix anything small, cut off, hidden, empty or off-zone.
   - Face close-ups use `closeup=True, keep=[face box]`.
   - Shots under a HUD use `top=250`.
   - Key props get `keep=[...]`.
   - `safezone.fit` runs inside `__main__` right before `render()`.
5. **Render and assemble**:
   ```bash
   O=output/<story>
   python3 animator/audio.py $O/sfx <TOTAL>
   (cd animator && python3 <story>.py ../$O/clips/animation.mp4 ../$O/cues.json)
   python3 assembler/assemble.py --clips $O/clips --voice <voice> --sfx $O/cues.json --sfx-dir $O/sfx \
     --music $O/sfx/music_game.wav --music-volume 0.4 --crf 20 --out $O/<story>_final.mp4
   ```
   No `--srt`, so there are no captions. For a late music start or a dip, call `audio.music_game(total, start=..., dips=[...])` and save it with `audio.save`.
6. **Measure** against the targets, and fix anything outside them before sending:
   - `python3 analysis/new_visuals.py $O/clips/animation.mp4`: a new visual every 1.1-1.6 s.
   - `python3 analysis/flow.py $O/clips/animation.mp4`: camera median 2-5, mean 6-11 (up to ~12 is fine), non-camera motion 5-8.
   - `python3 analysis/audio_ref.py $O/<story>_final.mp4 <subs.srt> $O/check`, against `sound_design.md` section 3:
     - music -10 ± 2.5 dB;
     - SFX 9-13 per 10 s;
     - SFX median -1 to -7 dB;
     - the music key reads G.
   - `python3 analysis/frame_log.py $O/<story>_final.mp4 <subs.srt> $O/fl 4`: look at every sheet.
7. **Send the mp4** to the user (SendUserFile). Commit and push the story code; `output/` is git-ignored. Say honestly what could not match.
8. **Fix requests:** patch only the shots or cues asked about. Edit those shot functions, keys or `SFX` entries, then re-render; a full render takes about 40 s per 20 s of video. `python3 <story>.py out.mp4 cues.json <first_frame> <last_frame>` renders only a frame range if needed. Never regenerate or redesign the rest.

## Defaults
- **No captions.** The references burn them in, but the user adds their own. If asked: `assemble.py --srt subs.srt --words 1 --font "Inter Display Black"`.
- **No lip-sync** (`engine.LIPSYNC = False`). The references change mouths by expression, not by phoneme.
- **No camera whoosh.** Only `whip.wav` on the loop rewind, and `swish` on a physical throw or a panel sliding in.
- **Hard cuts** (`render(xfade=0)`), grain 2, `vignette` 0.15 (flat vector look).
- `engine.DRIFT = (0.02, 5, -3)` and `engine.ENERGY = 3.0` (set at the top of the story).
- **Loop:** `render(..., fade_in=0, fade_out=0)` and the last shot draws the first frame.
- **Music:** `music_game` at `--music-volume 0.4`.
- **SFX:** about 1.1 per second, `SFX_GAIN = 0.17`, hits 1.3, booms 1.6 (see `sound_design.md`).

## Limits to state honestly
- This is 2D code animation. The references are hand-made vector animation with more drawing detail, bespoke props and smoother squash-and-stretch. We match the look (proportions, line, palette, shading, faces), and the pace, cuts, camera, phrase → visual logic and sound levels closely. Every new prop has to be drawn in code.
- Sounds are synthesised (`audio.py`). They match the measured kinds and levels, not the exact timbres of the reference channel's sound files, which must never be copied.
- The music matches the measured key, tempo, density and level. Its percussive share (0.07) is below the references' (0.14-0.22).
- `animator/thumbnail.py` is still the old kit's version (it imports `home`, `office`, `mom_owner`). Adapt it to `style.py` / `sets.py` when the user asks for a thumbnail (MASTER_PROMPT.md, "Thumbnail").

## New reference videos of this style
Run, for each video:
- `analysis/frame_log.py <video> [srt] <out> 4`
- `analysis/audio_ref.py <video> [srt] <out>` (needs the UVR model from `setup.sh`)
- `analysis/new_visuals.py <video>`
- `analysis/flow.py <video>`

Add what you learn to `visual_grammar.md` section 2, `sound_design.md` and `analysis/ref_data/`.
