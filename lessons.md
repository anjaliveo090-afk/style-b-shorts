# Lessons from YouTube analytics (read before every new script and every new video)

The user uploads each video to YouTube and sends back:
- the audience retention;
- where viewers swiped away (time + the line spoken);
- often why.

Each drop becomes a **lesson**: what went wrong, why, and a **rule** that every later script and video must follow. The rules here **override** `script_guide.md`, `visual_grammar.md` and the story templates when they conflict.

## How to handle an analytics message
0. **If the user sends the YouTube Studio export (zip of CSVs)**, run `python3 analysis/retention.py <zip> <video.mp4 or seconds> <subs.srt>` first. It converts the 1 % positions into seconds, groups the drop zones and prints the lines spoken there. Keep the export in `analysis/ref_data/analytics/<story>/`.
1. **Find the video.** Look up the YouTube title in `videos.md` to get the story name (`animator/<story>.py`, `output/<story>/`).
2. **For every drop point**, run `python3 analysis/drop_point.py <story> <time>`.
   - It prints the shot, the spoken lines and words, the SFX, the silence and the pace around the drop, and writes `output/<story>/drop_<t>.png`.
   - **Look at the frames.**
3. **Name the reason.**
   - If the user gave one, use it.
   - If not, find it with the checklist below. Several can apply; pick the main one and say how sure you are.
4. **Write the lesson** in the log below:
   - date, video, time, line, what happened, reason, the new **rule**, and where the rule applies (script / shots / sound / captions);
   - also copy the rule into the right section of `script_guide.md` or `visual_grammar.md` when it changes a general rule.
5. **Fix the system, not only the video.** If a template or tool caused it (e.g. `sample.py`, `captions.py`, `make_voice.py`), change it so the mistake cannot come back. Commit and push.
6. **Tell the user** in Hinglish: the reason, the rule, and what changes from the next video.

## How to diagnose a drop (checklist)
| # | Check | How to see it | Typical fix |
|---|---|---|---|
| 1 | **Weak first 1-2 s** (swipe before 3 s) | Is the first frame a big face, an absurd image, or text that makes the title promise visible at once? | A stronger first frame and first line; the payoff of the title shown in the first 1.5 s |
| 2 | **The visual sits still** | `drop_point` "last new visual" over ~2 s, or a long hold | More cuts: a new visual every 1.1-1.6 s |
| 3 | **Silence / slow voice** | "silence before the drop" over 0.5 s, or a slow, low-energy line | Tighten the voice; shorter lines; a reaction or SFX in the gap |
| 4 | **The visual does not match the words** | The frames show something other than what is said | A literal visual for the phrase |
| 5 | **Confusing beat** (viewers do not get the joke or the rule) | The line needs context, or the visual is too small or busy | Simplify: one clear subject, big, with a label |
| 6 | **Repetition** (same place, same joke, same card style again) | Similar frames to an earlier part | Change the location or angle; escalate instead of repeating |
| 7 | **Escalation stalls** (the stakes stop rising) | This chapter is not bigger than the last | Raise numbers ×100, a bigger place, a higher risk |
| 8 | **CTA / "subscribe" line** | The drop is on "Everyone who subscribes…" | Shorter, more visual, tied to the joke, or moved |
| 9 | **The ending is predictable** (drop near the end) | The twist is weak or guessable | A sharper twist; a faster loop line |
| 10 | **Audio problem** | SFX too loud or quiet, music over the voice, a robotic voice | Re-mix: `SFX_GAIN`, music volume, the voice tool |
| 11 | **Captions** cover the face or action, or repeat on-screen text | Look at the frames | Move or shorten the captions; `captions.py` rules |

## Rules learned (apply to every new script and video)
From "What If MOM Gave You 10 Seconds of Roblox" (16,820 viewers, 2026-11-04). Details in the log.

1. **Hook: the stake in the first frame and the first 1.5 s.** The first line is ≤ 1.8 s and carries the number/power ("What if Mom gave you TEN seconds of Roblox?", no filler like "only", "your"). The first frame is a giant close-up of the stake (the 0:10 clock in mom's hand, the Robux counter), never a wide room. In the first 3 s the picture changes every ≤ 0.8 s. *(script + shots)*
2. **First chapter by ~5 s.** The setup is at most 3 short lines (≤ 4 s in total); "Day 1" / "Second 10" starts by 5 s. The 10 s video bled 1-1.5 % of viewers every half second through a 7 s setup. *(script)*
3. **The subscribe CTA is never a chapter of its own.** One line, ≤ 2 s. **Right before it, open a curiosity loop** ("But at second five, something impossible happens…") and **pay it off right after it** with the biggest surprise so far. Never put it on a lull. The 10 s video lost 10.5 % in the 2.5 s after "Second 6, everyone who subscribes gets a golden crown." *(script)*
4. **The payoff is the last thing.** The comment CTA comes **before** the final beat (≤ 1.5 s), or only as the on-screen comments sheet with no voice. The last spoken line is the punchline and it must lead straight back into the hook (the loop). No silence over 0.4 s in the last 5 s. The 10 s video lost 19.6 % on "Comment loop if…", spoken after the story had ended and after a 0.76 s silence. *(script + shots + voice)*
5. **No chapter line longer than ~2.5 s.** Split long lists ("You buy every game pass. [break] Even the toaster one."). *(script)*
6. **Keep what worked:** the countdown climax and the "Then you find… THIS!" discovery had almost no drop (≤ 0.5 % per position from 32 to 46 s), and the loop made 150 % retention at the start (many rewatches). Curiosity + a reveal holds viewers; keep one in every video. *(script)*

## Log
| Date | Video (story) | Time | Line | What happened | Reason | Rule added |
|---|---|---|---|---|---|---|
| 2026-11-04 | What If MOM Gave You 10 Seconds of Roblox (`analysis/ref_data/analytics/tensec`) | 0-6 s | "What if your mom only gave you 10 seconds of Roblox?" / "10 seconds, then you go to bed." | 25 % gone by 2.5 s, then 1-1.5 % every half second until 6 s (32 % in all) | Partly the normal Shorts swipe. On top: after a 0.5 s blurred slam, the frame is one wide room shot with small characters for 2 s; the stake (10 s) is only in the caption and a small clock; the first chapter starts at 10 s. **Medium confidence** | 1, 2 |
| 2026-11-04 | same | 17.5 s | "One punch, KO!" → "Second 8…" | 1.0 % | a small dip between chapters; **low confidence** | – |
| 2026-11-04 | same | 28-30.5 s | "Second 6, everyone who subscribes gets a golden crown." (24.8-27.7) → "Second 5, you hatch the rarest pet…" | **10.5 %** in 2.5 s; flat before it (0.2-0.5 % per position) | The CTA took a whole countdown step (3 s) with nothing new for the story; the next beat (a pet hatch) did not promise more. Viewers decide during the ask and swipe just after it. **High confidence** | 3, 5 |
| 2026-11-04 | same | 47-49 s | "Plus 10 seconds. Not again!" → 0.76 s silence → "Comment loop if you watch this more than once." | **19.6 %** left before the last word | The story was over at 46.3 s; the comment ask after it gave a reason to leave instead of looping. **High confidence** | 4 |
