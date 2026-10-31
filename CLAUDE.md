# Project: Style B "blocky game" animated Shorts

This repo turns a voiceover + SRT into a 9:16 animated Short in one fixed style: flat-vector blocky game avatars, a navy night bedroom and bright game worlds, game UI, hard cuts, punch-ins on key words, loud punchy SFX over a cheeky G-centred game tune.

Everything is drawn in code: pycairo frames → ffmpeg. There is no AI video model.

When the user gives a voiceover + SRT (or a script), follow this workflow without being asked.

## Titles and scripts (before any voice exists)
Read `script_guide.md` first. It was learned from 6 reference videos: who speaks when, the emotions, the beat sheet and the silent parts.
- **"Title do" / "titles":**
  - Give 10 titles from the formulas in section 1, and mark the 3 strongest.
  - Our own ideas only; never the reference channel's titles.
- **"Is title se script likho":**
  - Write a script in the user's format (`Narrator: [emotion] … [break] …`, then `Mom: [angry] …` blocks).
  - Follow the 14-beat sheet (section 2): 120-145 words, emotion tags from section 4, and pause tags kept short (section 3).
  - After the script, give a 1-line speaker list and the estimated length.
- **"Voice banao" (test voice):**
  - Run `python3 assembler/make_voice.py <script.txt> output/<story> --model <kokoro.onnx> --voices <voices.bin>`. The model files come from github.com/thewh1teagle/kokoro-onnx releases `model-files-v1.0`; install with `pip install kokoro-onnx`.
  - It writes `voice.mp3`, `subs.srt` and `speakers.json` (who speaks when, used for lip-sync), with one voice per character and the pauses kept short.
  - Kokoro cannot act emotions: the tags only change speed, volume and pitch. Say so; the user's own voice tool is better for final videos.
- **Another topic or script:** bend it into the reference topic world with section 5 (Roblox + family antagonist + Day ladder + zero-crash + twist + loop). Keep the user's core idea.

## Read first
| File | What it holds |
|---|---|
| `style_bible.md` | Look: format and safe zone, characters in head-widths, faces and the 19 expressions, palette, sets, STYLE LOCK |
| `visual_grammar.md` | Measured pace and camera; **section 2 = phrase type → what is shown → camera → reaction** (rows 1-20) |
| `sound_design.md` | Measured music and SFX, the mix defaults and the target numbers |
| `script_guide.md` | Titles, the script format with characters and emotions, the 14-beat sheet, bending other topics, and the measured silent parts (what is on screen during them) |
| `animator/sample.py` | **The template story.** Copy it for every new video |
| `animator/style.py` | Characters: `Block` (same `draw()` signature as the old `style2.Char2`), the cast `KID`, `KID_GAME`, `MOM`, `MOM_ROBE`, `DAD`, `GRANDMA`, `NOOB`, `BOSS`, `crowd_member(i)`, `back_figure`, and the FX `sweat`, `anger_mark`, `shake_lines`, `sparkle` |
| `animator/sets.py` | Places, props, game UI and FX (list at the top of the file) |
| `animator/audio.py` | Synthesised SFX + `music_game()` |
| `animator/engine.py` | Camera keys and render. Do not change unless broken |
| `animator/safezone.py` | Keeps characters, labels and `keep` boxes in the Shorts safe zone |

`reference_examples/` is the older toolkit this repo was built from (another style). Read it only for method; never import from it.

## Workflow for a new voice + SRT
0. **Silences.** Run `python3 analysis/silences.py - <voice> - <subs.srt> output/<story>/silences`.
   - If any gap is over 0.8 s, or the voice runs below ~88% of the time, tighten it first: `python3 assembler/tighten_voice.py <voice> <subs.srt> output/<story>/voice.wav output/<story>/subs.srt --max 0.6`.
   - Then use the tightened voice and SRT from here on.
   - Plan a visual for every gap (`script_guide.md` section 6): the next cut or card starts in the gap, a reaction snap plus one SFX goes on the punchline, and a reveal gets a creeping push.
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
   - Keep its helpers: `shot`, `punch`, `kid_face` / `FACE_*` close-ups, `SFX_GAIN`, `MUSIC`, `TOTAL`, the loop ending (`s_end` = first frame), and the `__main__` block (it writes `cues.json` and `music.wav`).
   - `animator/report_noob.py` is a second, full 60 s example (48 shots). Its helpers include `closeup()`, a named game character with a name tag, a developer at a desk, and the report/ban props.
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
     --music $O/music.wav --music-volume 0.5 --crf 20 --out $O/<story>_final.mp4
   ```
   - No `--srt` here: the captions are burned afterwards with `assembler/captions.py` (step 7).
   - The story writes `music.wav` from its `MUSIC` settings (a late start, dips under dramatic beats).
   - A 60 s render takes about 1.5 min.
6. **Measure** against the targets, and fix anything outside them before sending:
   - `python3 analysis/new_visuals.py $O/clips/animation.mp4`: a new visual every 1.1-1.6 s.
   - `python3 analysis/flow.py $O/clips/animation.mp4`: camera median 2-5, mean 6-11 (up to ~12 is fine), non-camera motion 5-8.
   - `python3 analysis/audio_ref.py $O/<story>_final.mp4 <subs.srt> $O/check`, against `sound_design.md` section 3. If the SFX median is off, change only `SFX_GAIN`, rewrite `cues.json` and re-assemble; no re-render is needed:
     `(cd animator && python3 -c "import json, <story> as r; json.dump([{'time': round(t, 3), 'file': f, 'volume': round(v * <GAIN>, 3)} for t, f, v in sorted(r.SFX)], open('../$O/cues.json', 'w'))")`.
     Results:
     - music -10 ± 2.5 dB;
     - SFX 9-13 per 10 s;
     - SFX median -1 to -7 dB;
     - the music key reads G.
   - `python3 analysis/frame_log.py $O/<story>_final.mp4 <subs.srt> $O/fl 4`: look at every sheet.
7. **Burn the captions** (see Defaults), then **send only `<story>_final_captions.mp4`** to the user (SendUserFile), one file. Commit and push the story code; `output/` is git-ignored. Say honestly what could not match.
8. **Fix requests:** patch only the shots or cues asked about. Edit those shot functions, keys or `SFX` entries, then re-render; a full render takes about 40 s per 20 s of video. `python3 <story>.py out.mp4 cues.json <first_frame> <last_frame>` renders only a frame range if needed. Never regenerate or redesign the rest.

## Defaults
- **Captions are ON by default, and only ONE video is delivered: the captioned one** (the user's rule, to save credits). Never send a caption-free copy unless the user asks for it. Burn reference-style captions onto the finished mp4 without re-rendering:
  1. Write `animator/captions/<story>.json`: `[[first_word_index_or_time, "TEXT", colour or null], ...]`, one entry per caption, using the rules in `style_bible.md` section 1 (example: `animator/captions/no_break.json`).
  2. Run `python3 assembler/captions.py $O/<story>_final.mp4 $O/words/aligned.json animator/captions/<story>.json $O/<story>_final_captions.mp4 animator/<story>.py`. Use `auto` instead of the JSON for a quick automatic version.
     - The last argument (the story) is **always passed**: the user asked that text already on screen is never repeated in a caption.
     - The tool replays the story, records every label, chapter card, bubble, HUD and UI text visible during each caption, and removes those words. A caption left with only filler words is dropped.
     - It prints every caption it removed or shortened; check the list.
  3. Keep the scene labels out of the caption band (y 760-890): move any label there to the top.
- **Lip-sync only on character dialogue** (the user's rule): narrator lines get no mouth movement, but when a character speaks (quotes in the script, e.g. "Whose card did you use?"), that character's mouth follows the voice.
  - Set `engine.LIPSYNC = True` and a `DIALOGUE = {"mom": [(t0, t1)], ...}` dict from the SRT.
  - Draw the speaker with `talk=talking("mom", T)` and call `engine.set_voice(voice)` in `__main__` (see `animator/robux10.py`).
  - Mouths snap between closed, half open and wide open.
- **No camera whoosh.** Only `whip.wav` on the loop rewind, and `swish` on a physical throw or a panel sliding in.
- **Hard cuts** (`render(xfade=0)`), grain 2, `vignette` 0.15 (flat vector look).
- `engine.DRIFT = (0.02, 5, -3)` and `engine.ENERGY = 3.0` (set at the top of the story).
- **Loop:** `render(..., fade_in=0, fade_out=0)`. The last 0.5-1.0 s after the final word is a REWIND montage, as in the references:
  - `draw, ov = sets.rewind_shot(SHOTS, [t1, t2, …, 0.0])` plays 4-6 earlier shot times backwards and lands exactly on the first frame.
  - Use it as the last shot with keys `[(start, 1.0, (360, 640))]`, `overlay=ov`, `blur=False`, `closeup=True`, `keep=[]`.
  - Add `whip.wav` at its start.
- **Music:** `music_game` (`MUSIC` dict in the story) at `--music-volume 0.5`.
- **SFX:** about 1.1 per second, `SFX_GAIN = 0.4` for a real recorded voice (the TTS sample needed 0.17), hits 1.3, booms 1.6. Always measure and adjust (see `sound_design.md`).

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
