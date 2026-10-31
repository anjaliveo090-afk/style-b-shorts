# Lessons from YouTube analytics (read before every new script and every new video)

The user uploads each video to YouTube and sends back:
- the audience retention;
- where viewers swiped away (time + the line spoken);
- often why.

Each drop becomes a **lesson**: what went wrong, why, and a **rule** that every later script and video must follow. The rules here **override** `script_guide.md`, `visual_grammar.md` and the story templates when they conflict.

## How to handle an analytics message
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
*(empty: the first analytics have not arrived yet)*

## Log
| Date | Video (story) | Time | Line | What happened | Reason | Rule added |
|---|---|---|---|---|---|---|
