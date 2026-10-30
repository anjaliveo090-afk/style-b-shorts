# Master prompt: new voice + SRT → Style B animated Short

Open a new Claude Code chat on this repository, from any device (claude.ai/code or the Claude app → Code).
1. Attach your voiceover (mp3/wav) and its SRT.
2. Paste the text inside the box below and send it.

```
I am attaching a voiceover and its SRT. Make a 9:16 animated Short from it in exactly
this repository's style (Style B: blocky game avatars, night bedroom + game worlds,
hard cuts, punch-ins on key words, loud punchy SFX, cheeky G-centred game music).

SETUP
- Run `bash setup.sh` (installs packages, ffmpeg, fonts and the analysis model).
- Read these first and follow them strictly:
  CLAUDE.md, style_bible.md, visual_grammar.md (all sections, especially 2 and 3),
  sound_design.md (section 3 = mix defaults and targets), assembler/README.md.
- Characters: animator/style.py (Block, cast KID / KID_GAME / MOM / MOM_ROBE / DAD /
  GRANDMA / NOOB / BOSS, crowd_member). Places, props, game UI, FX: animator/sets.py.
- Template to copy: animator/sample.py (hard cut per phrase, punch-in keys on key words,
  face close-ups with closeup=True + keep=FACE_KEEP, DAY/SECOND chapter text, game UI,
  SFX list with SFX_GAIN, loop ending on the first frame).
  Do not change engine.py / style.py unless something is broken; add new places to sets.py.

STEP 1 - WORDS
- Strip any "(Transcribed by ...)" text from the SRT.
- Run `python3 analysis/align_words.py <voice> <subs.srt> output/<story_name>/words` for word timings.

STEP 2 - VISUAL PLAN
- Split the narration into phrases of 2-4 words.
- Tag each phrase with a row from visual_grammar.md section 2 (rows 1-20).
- Show what is SAID, literally:
  - an object or prop for each noun;
  - a counter for numbers;
  - a "DAY N" / "SECOND N" card for chapters;
  - a big red X for "no / wrong";
  - a face close-up (closeup=True) for reactions;
  - game UI (stage pill, health bar, leaderboard, shop, comments) for game things.
- A hard cut on each phrase, a new visual every 1.1-1.6 s. The camera punches in (0.1-0.2 s key)
  and expressions snap ON the key word.
- Show me the plan as a table (time | words | row | visual | camera | expression | SFX) before building.
- Safe zone: the WHOLE character and key props inside x 38-680, y 149-1013
  (below y 678 only up to x 599). Face close-ups keep the face and labels inside.
  safezone.fit(SHOTS, sys.modules[__name__]) runs right before render().

STEP 3 - BUILD AND CHECK FRAMES
- Write animator/<story_name>.py (copy sample.py). Add new places or props to animator/sets.py.
- Before the full render, run `cd animator && python3 contact.py <story_name> ../output/<story_name>/contact.png 1`
  and look at it. Fix anything small, cut off, hidden, empty or outside the red safe-zone outline.

STEP 4 - MY DEFAULTS
- No captions (do not pass --srt to assemble.py). No lip-sync. No camera whoosh.
- Hard cuts: render(xfade=0, grain=2, fade_in=0, fade_out=0), loop back to the first frame.
- Music: audio.music_game() → music_game.wav at --music-volume 0.4.
- SFX: about 1.1 per second on visual events, SFX_GAIN = 0.17, hits 1.3, booms 1.6.
- Synthesised SFX and music only (animator/audio.py).

STEP 5 - MEASURE, THEN SEND
- analysis/new_visuals.py: a new visual every 1.1-1.6 s.
- analysis/flow.py on the animation: camera median 2-5, mean 6-11; non-camera motion 5-8.
- analysis/audio_ref.py on the final mp4:

  | Measure | Target |
  |---|---|
  | Music vs voice | -10 ± 2.5 dB |
  | Music key | G (major or minor) |
  | SFX per 10 s | 9-13 |
  | SFX median vs voice | -1 to -7 dB |
  | SFX on a visual change | above the random share |

- analysis/frame_log.py on the final mp4: look at every sheet.
- Send me the final mp4, and commit and push the code (output/ is git-ignored).
- Tell me honestly what could not match the reference.
- For fixes later: patch only the needed shots, never regenerate everything.
```

## Thumbnail (only when you ask for one)
Send: `Make the thumbnail for this video.` Claude will adapt `animator/thumbnail.py` to Style B:
- one huge emotional face (`style.Block` at a big scale) and a clear opponent;
- 2-3 words of text in Inter Black with a thick outline;
- a bright burst (`sets.burst`);
- 1080x1920 for Shorts and 1280x720 for search.

Style B has no white sticker outline around characters, so `--no-stroke` is the default variant.

## Notes
- Everything is on `main`, so no branch checkout is needed.
- The reference videos are not needed again. Their analysis lives in:
  - `style_bible.md`
  - `visual_grammar.md`
  - `sound_design.md`
  - `analysis/ref_data/`
- To skip `setup.sh` in every new chat, paste `bash setup.sh` into the cloud environment's
  **Setup script** (session title bar → environment menu → Edit).
- A ~50 s video takes about 20-40 minutes in total: planning, new props, a ~1.5 min render, then checks.
