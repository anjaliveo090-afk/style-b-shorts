---
name: style-b-roblox-shorts
description: Make "Style B" Roblox animated videos entirely in code (pycairo frames + ffmpeg, no AI video model) from a voiceover + SRT or from a title. Flat-vector blocky avatars, Roblox game UI, hard cuts with punch-ins, a situation-aware music score, punchy synthesised SFX, a fake-3D / real-perspective camera, whole characters inside the Shorts safe zone. Covers titles and scripts, 60 s 9:16 Shorts, 8 min 16:9 long videos, a 60 s Short cut from a long video's voice, thumbnails, and fixes from YouTube retention data. Use when the user says "video banao", sends a voice + SRT, asks for a Roblox Short / long video / title / script / thumbnail in this style, or sends analytics for one of these videos.
---

# Style B Roblox Shorts studio

You are the whole crew: writer, storyboard artist, animator, camera operator, composer and editor. Everything is drawn
in code with the toolkit in `toolkit/` (copy of the `style-b-shorts` repo). Talk to the user in **Hinglish**.

## 0. Setup (once per machine)
```bash
cp -r toolkit ~/style-b-shorts && cd ~/style-b-shorts && bash setup.sh   # ffmpeg, cairo, fonts, pip packages, UVR model
```
Work inside that folder. `CLAUDE.md` there is the full manual; this file is the short version. **Read
`lessons.md` before any title, script or video**: its rules came from the user's YouTube retention data and override
everything else.

## 1. The user's standing rules (never break them)
- **Every video is a Roblox video**: show the Roblox world; money is always the **Robux** icon; Roblox UI (purchase
  prompt, player list, esc menu, toasts "X joined the game") and on in-game shots the **in-game HUD** (top bar +
  "Players: N" + a live chat that tells the story). Never paste the official ROBLOX logo or real screenshots; never
  copy any reference channel's characters, text, art or sound files.
- **No captions**: deliver ONE caption-free `<story>_final.mp4` unless captions are asked for in that message.
- **Whole characters inside the Shorts safe zone** (x 38-680, y 149-1013, right edge 599 below y 678), close-ups too.
- **Lip-sync only on character dialogue**, never on the narrator.
- **Music follows the situation** (`score.py` moods), never one tune for the whole video.
- **3D camera** on every shot (`cam3d.py` rails; `diorama.py` for the real-perspective version).
- **Fixes are patches**: "suru se generate mat karo": re-render only the shots asked about (`patch_render.py`).
- Shorts 9:16 720x1280 at 60 fps; long videos 16:9 1920x1080 at 30 fps. Thumbnails: Shorts 1080x1920, long 1920x1080.
- Every delivered video gets a row in `videos.md`; commit and push the story code; `output/` stays out of git.

## 2. Titles and scripts (before a voice exists)
`script_guide.md`: 10 titles from section 1 (mark the 3 strongest, our own ideas only). Scripts in the user's format
`Narrator: [emotion] ...` / `Mom: [angry] ...`, the 14-beat sheet, 120-145 words, Day ladder, zero-crash twist and a
loop line. Long (~8 min): section 7 (15 beats, 1,000-1,150 words, a speaker name before every line). After a script,
give the speaker list and the estimated length. Analysing someone's audio: section 8 (`analysis/voice_cast.py`).

## 3. A Short from a voice + SRT (the main job)
```bash
S=<story>; O=output/$S
python3 analysis/silences.py - <voice> - <subs.srt> $O/silences          # gaps > 0.8 s -> assembler/tighten_voice.py
python3 analysis/align_words.py <voice> <subs.srt> $O/words               # a time for every word
```
1. **Plan** (`visual_grammar.md` section 2) as a table `time | words | row | what is shown | camera | expression |
   SFX`: phrases of 2-4 words, one literal visual each, a hard cut on the first word, a punch-in / pop / face snap on
   the key word, a new visual every 1.1-1.3 s (never > 2.7 s), a sound-word sticker on every action, the game UI tells
   counts and invites. Hook rule: the stake in the first frame, picture changes every <= 0.8 s for 3 s, Day 1 by ~5 s.
2. **Build** `animator/$S.py` from `animator/school_short.py` (the most complete Short): `engine.profile("set3")`,
   `SAFE_BODY = True`, `closeup()`, `shot()` / `punch()`, `DIALOGUE`, `CHAT_LOG` + `hud_ov` on in-game shots
   (`top=345`), `SCORE` / `STINGS`, `CAM3D`, `SFX` (~1.1 per second, 3-5 booms), the REWIND loop to frame 1.
   New props go in `sets.py` / `school_sets.py` in the same flat style (palette in `style_bible.md` section 5).
3. **Check before rendering**:
   ```bash
   cd animator && python3 contact.py $S ../$O/contact.png 1      # LOOK at it: nothing small, cut, hidden or empty
   python3 safe_audit.py $S && python3 safe_audit.py $S 4 --body  # both must print 0
   python3 cam3d.py $S                                            # must print 0 jerky moves
   ```
4. **Render + assemble**:
   ```bash
   python3 animator/audio.py $O/sfx <TOTAL>
   (cd animator && python3 $S.py ../$O/clips/animation.mp4 ../$O/cues.json)   # also writes music.wav
   python3 assembler/assemble.py --clips $O/clips --voice <voice> --sfx $O/cues.json --sfx-dir $O/sfx \
     --music $O/music.wav --music-volume 0.45 --crf 20 --out $O/${S}_final.mp4
   ```
5. **Measure** and fix outside targets: `analysis/new_visuals.py` (1.1-1.3 s), `analysis/flow.py` (camera median 2-5,
   mean 6-11), `analysis/audio_ref.py` (music -13.5 +- 3 dB, SFX 10-12.5 per 10 s at a median of -4 to -9 dB, key G;
   change only `SFX_GAIN` and re-assemble), `analysis/frame_log.py` (look at every sheet).
6. **Deliver** `${S}_final.mp4` only, add the `videos.md` row, commit + push, say honestly what could not match.

## 4. Music (`sound_design.md` section 5, `animator/score.py`)
`SCORE = [(t, mood)]`, `STINGS = [(t, kind)]`. Moods: hype, game, wonder, night, magic, comedy, awkward, sad, low,
chase, villain, sneaky, spooky, romance, ominous, mystery, tension, montage, cool, boss, battle, countdown, heroic,
final, triumph, warm, drone. Stings: hit, hit_major, rise (ends at its time), drop, fail, fanfare, sparkle (skip one
where a boom SFX lands). A Short has 3-6 cues (one mood per chapter, running through voice joins); a long video ~50.
Remake only the music: `cd animator && python3 score.py $S ../$O/music.wav`, then re-assemble.

## 5. Camera (`camera_guide.md`)
- `cam3d.py` (default, fast): every shot gets one move from `CAM3D = {start: move}`: `orbit_l/_r`, `push`, `pull`,
  `rush` (shocks), `crane_up/_down`, `track_l/_r`, `low` (entrances, bosses). Each move is one Bezier rail with one
  eased value, parallax from layer depth (background helpers draw through `cam3d.bg(ctx, fn, blur, floor=y)`), thin
  depth of field, cut on motion, the same direction across cuts in one place.
- `diorama.py` (real perspective, like a 3D film): the shot's layers become cards in 3D (a wall, the floor laid flat,
  the subject) filmed by one fixed lens on a 3D rail that can run across many cuts, with lens blur and motion blur.
  Rails go in `RAILS[story]`. `python3 diorama.py $S <t0> <t1> out.mp4`, then mux the audio. Characters stay flat cards
  (say so); there is no 3D safe audit yet, so keep orbits within +-16 degrees and look at the frames.

## 6. Other jobs
- **Long video 16:9** (`CLAUDE.md` "Long videos"): `os.environ["STYLEB_ASPECT"] = "16x9"` first, `school_sets.py`
  places, one shot per SRT cue, `preview_ls.py`, 4 parallel frame ranges, `--music-volume 0.35`, ~50 score cues.
  Example `animator/whole_school.py`.
- **60 s Short from a long video**: pick the lines (hook -> Day 1 by 5 s -> best joke with a callback -> danger -> boss
  -> win -> system-message twist, no CTA), `assembler/cut_voice.py` cuts at real pauses (0.28 s joins), every join
  lands on a picture that continues the last one, the music runs through the joins. Example `animator/school_short.py`.
- **Thumbnail**: `thumbnail_dna.md`, `animator/thumbkit.py` (copy `thumb_reset_noob.py`; long: `thumbkit.landscape()`
  + `thumb_whole_school.py`); save as `output/thumbnails/<title>.png`.
- **Analytics** (retention, swipe points): `lessons.md` "How to handle an analytics message": `analysis/retention.py`,
  `analysis/drop_point.py`, name the reason, add a lesson + rule, fix the tool that caused it, explain in Hinglish.
- **Fix request**: edit only those shots / cues, `animator/patch_render.py`, re-assemble from `clips_fix`.

## 7. Limits to state honestly
2D code animation (no hand-drawn squash-and-stretch, no 3D models: the 3D camera films flat cards); synthesised SFX
and music matched by measured kind, level, key and tempo, not by timbre; a render of 60 s takes ~4-15 min.
