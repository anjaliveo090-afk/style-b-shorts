"""Situation score: background music that follows the story (the user's rule, 2026-11-07: "background music
situation ke hisaab se").

music_game() plays one cheeky G tune under the whole video. A long video needs the music to change with what is
happening: a music box at night, a bouncy tuba under a joke, a ticking mystery, a heavy boss theme, a heartbeat at the
low point, a fanfare when it is won. music_score() takes a cue list [(time, mood), ...] and starts each mood on its own
downbeat at that time (a hard music cut, like the picture), letting the last notes of the old mood ring out for a
moment. One-shot stings [(time, kind), ...] mark the big beats: a hit on a reveal, a riser into it, a power-down on a
blackout, a sad trombone on a fail, a fanfare on a win.

Every mood stays centred on G (G major when happy, G minor when tense or sad, G dorian when cool), so the score still
reads as G (sound_design.md section 1). All attacks are >= 8 ms and nothing is noise, so analysis/audio_ref.py does not
count the music as SFX. The music never stops completely (script_guide.md: the references never go silent): a "stop"
is the quiet "drone" mood.

Levels: every mood is normalised to the steady level of music_game (RMS 0.063, the level the earlier mixes were
checked at) and then offset by MOODS[name]["db"], so quiet moods sit lower under emotional lines and battles sit a
little higher. Mix with assemble.py --music-volume 0.35 for long videos, as before.

Run (from animator/):
  python3 score.py <story> <out.wav>   the story defines TOTAL, SCORE = [(t, mood), ...], STINGS = [(t, kind), ...]
  python3 score.py --demo <out_dir>    8 s of every mood and every sting, to listen to
"""
import os
import sys
import wave

import numpy as np

from audio import SR, note, tt

TWO_PI = 2 * np.pi
LEVEL = 0.063                     # steady RMS of music_game, the level the old mixes were measured with


# ---------- instruments (attacks >= 8 ms, no noise) ----------
def _att(t, a):
    return np.minimum(1.0, t / a)


def _rel(t, d, r):
    return np.clip((d - t) / r, 0.0, 1.0)


def _sin(f, t, ph=0.0):
    return np.sin(TWO_PI * f * t + ph)


def marimba(f, d=0.5):
    t = tt(d)
    return (_sin(f, t) + 0.25 * _sin(4 * f, t) * np.exp(-t * 30)) * np.exp(-t * 9) * _att(t, 0.008)


def square(f, d=0.3, decay=9.0):
    t = tt(d)
    x = sum(_sin(f * h, t) / h for h in (1, 3, 5, 7, 9) if f * h < 15000)
    return x * _att(t, 0.008) * np.exp(-t * decay) * _rel(t, d, 0.02)


def bass(f, d):
    t = tt(d)
    x = _sin(f, t) + 0.35 * _sin(2 * f, t) + 0.12 * _sin(3 * f, t)
    return x * _att(t, 0.07) * np.exp(-t * 1.5) * _rel(t, d, 0.05)


def celesta(f, d=1.4):
    t = tt(d)
    x = _sin(f, t) + 0.3 * _sin(4 * f, t) * np.exp(-t * 20) + 0.12 * _sin(2 * f, t)
    return x * np.exp(-t * 3.2) * _att(t, 0.008) * _rel(t, d, 0.05)


def pad(f, d, att=0.35):
    t = tt(d)
    x = (_sin(f, t) + _sin(f * 1.004, t, 1.0) + _sin(f * 0.996, t, 2.0)) / 3 \
        + 0.22 * _sin(2 * f, t) + 0.08 * _sin(3 * f, t)
    return x * _att(t, att) * _rel(t, d, 0.45)


def brass(f, d, decay=1.0):
    t = tt(d)
    x = sum(_sin(f * h, t) / h * (1.0 if h <= 2 else np.exp(-t * h * 0.9)) for h in range(1, 8) if f * h < 15000)
    return x * _att(t, 0.02) * np.exp(-t * decay) * _rel(t, d, 0.06)


def tuba(f, d=0.3):
    t = tt(d)
    x = sum(_sin(f * h, t) / h ** 1.4 for h in range(1, 5))
    return x * _att(t, 0.015) * np.exp(-t * 5) * _rel(t, d, 0.04)


def pizz(f, d=0.35):
    t = tt(d)
    return sum(_sin(f * h, t) * np.exp(-t * (10 + h * 4)) / h for h in range(1, 5)) * _att(t, 0.008)


def guitar(f, d=0.9):
    t = tt(d)
    x = sum(_sin(f * h, t) * np.exp(-t * (3.5 + h * 2)) / h for h in range(1, 5))
    return x * _att(t, 0.008) * _rel(t, d, 0.05)


def epiano(f, d=1.2):
    t = tt(d)
    x = _sin(f, t) + 0.18 * _sin(2 * f, t) + 0.25 * _sin(7 * f, t) * np.exp(-t * 25)
    return x * np.exp(-t * 2.2) * (1 + 0.12 * np.sin(TWO_PI * 5 * t)) * _att(t, 0.008) * _rel(t, d, 0.06)


def _phase(f, t, rate, depth, glide=0.0):
    inst = f * (1 + depth * np.sin(TWO_PI * rate * t)) * (1 - glide * np.exp(-t * 12))
    return TWO_PI * np.cumsum(inst) / SR


def violin(f, d):
    t = tt(d)
    ph = _phase(f, t, 5.5, 0.006 * np.minimum(1, t / 0.3))
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + 0.08 * np.sin(4 * ph)
    return x * _att(t, 0.12) * _rel(t, d, 0.2)


def theremin(f, d):
    t = tt(d)
    ph = _phase(f, t, 6.2, 0.014, glide=0.06)
    return (np.sin(ph) + 0.1 * np.sin(2 * ph)) * _att(t, 0.06) * _rel(t, d, 0.15)


def kick(d=0.3):
    t = tt(d)
    f = 52 + 75 * np.exp(-t * 32)
    return np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t * 13) * _att(t, 0.008)


def wood(f=1250, d=0.09):
    t = tt(d)
    return (_sin(f, t) + 0.4 * _sin(2.7 * f, t)) * np.exp(-t * 55) * _att(t, 0.008)


def tom(f=110, d=0.35):
    t = tt(d)
    fr = f * (1 + 0.6 * np.exp(-t * 25))
    return np.sin(TWO_PI * np.cumsum(fr) / SR) * np.exp(-t * 9) * _att(t, 0.008)


def timp(f=49, d=1.6):
    t = tt(d)
    ph = TWO_PI * np.cumsum(f * (1 + 0.25 * np.exp(-t * 12))) / SR
    x = np.sin(ph) + 0.45 * np.sin(1.5 * ph) + 0.25 * np.sin(2 * ph)
    return x * np.exp(-t * 2.2) * _att(t, 0.01)


# ---------- chords: (bass midi, lead tones midi), all around G ----------
CH = dict(
    G=(43, [67, 71, 74, 79]), Gm=(43, [67, 70, 74, 79]), Eb=(39, [67, 70, 75, 79]), D7=(38, [66, 69, 72, 74]),
    C=(36, [67, 72, 76, 79]), Cm=(36, [67, 72, 75, 79]), D=(38, [66, 69, 74, 78]), Em=(40, [67, 71, 76, 79]),
    Bm=(47, [66, 71, 74, 78]), Bb=(46, [70, 74, 77, 82]), F=(41, [65, 69, 72, 77]), Ab=(44, [68, 72, 75, 80]),
    DF=(42, [66, 69, 74, 78]), Gmaj7=(43, [66, 67, 71, 74]), Cmaj7=(36, [64, 67, 71, 76]),
    Am7=(45, [67, 69, 72, 76]), D9=(38, [66, 69, 72, 76]), Gm7=(43, [65, 67, 70, 74]), C7=(36, [64, 67, 70, 76]),
)

R_HYPE = [[0, None, 2, 1, None, 3, None, 2], [None, 1, None, 2, 3, None, 2, None],
          [0, None, 1, None, 2, None, 3, None], [3, None, 2, None, 1, 0, None, None]]
R_GAME = [[0, None, 2, None, None, None, None, None], [None, None, None, 2, 1, None, None, None],
          [0, None, None, None, None, 3, None, None], [3, None, None, None, 1, None, None, None]]
R_COMEDY = [[0, None, 1, 2, None, 3, None, None], [3, None, 2, None, 1, None, 0, None],
            [None, 0, 1, None, 2, None, 3, 2], [3, 2, None, 1, None, 0, None, None]]


# ---------- moods: one bar each. P(sound, time, gain); t bar start; b beat length; ch chord; n bar no.; q 0..1 ----------
def _hype(P, t, b, ch, n, q):
    root, tones = ch
    for k in range(8):
        P(bass(note(root + (12 if k % 2 else 0)), b * 0.45), t + k * b / 2, 0.16)
    for k, i in enumerate(R_HYPE[n % 4]):
        if i is not None:
            P(marimba(note(tones[i])), t + k * b / 2, 0.3)
            P(square(note(tones[i] + 12), 0.25), t + k * b / 2, 0.07)
    for k in range(4):
        P(kick(), t + k * b, 0.3)
        P(wood(1500 if k % 2 else 1250), t + k * b + b / 2, 0.07)


def _game(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 1.9), t, 0.2)
    P(bass(note(root + 7), b * 1.9), t + 2 * b, 0.13)
    for k, i in enumerate(R_GAME[(n // 4 + n) % 4]):
        if i is not None:
            P(marimba(note(tones[i])), t + k * b / 2, 0.3)
            P(square(note(tones[i] + 12), 0.3), t + k * b / 2, 0.07)
    for k in (0, 2):
        P(kick(), t + k * b, 0.19)
    for k in range(4):
        P(wood(1500 if k % 2 else 1250), t + k * b + b / 2, 0.042)


def _wonder(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 1.9), t, 0.15)
    P(bass(note(root), b * 1.9), t + 2 * b, 0.1)
    P(pad(note(tones[0] - 12), b * 4), t, 0.04)
    P(pad(note(tones[2] - 12), b * 4), t, 0.03)
    for k, i in enumerate([0, 1, 2, 3, 2, 3, 1, 2]):
        P(celesta(note(tones[i] + 12), 0.8), t + k * b / 2, 0.09)
    P(kick(), t, 0.18)
    P(kick(), t + 2 * b, 0.12)


def _night(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 3.9), t, 0.12)
    P(pad(note(tones[0] - 12), b * 4), t, 0.04)
    P(pad(note(tones[2] - 12), b * 4), t, 0.03)
    mel = [[(0, 3), (1.5, 2), (2, 1)], [(0, 2), (2, 1), (3, 0)], [(0, 3), (1, 2), (1.5, 1), (3, 2)], [(0, 1), (2, 0)]]
    for pos, i in mel[n % 4]:
        P(celesta(note(tones[i] + 12), 1.6), t + pos * b, 0.1)


def _magic(P, t, b, ch, n, q):
    """A wish being granted: a 16th celesta arpeggio that climbs and swells."""
    root, tones = ch
    g = 0.45 + 0.55 * q
    P(pad(note(tones[0] - 12), b * 4), t, 0.05 * g)
    P(pad(note(tones[2] - 12), b * 4), t, 0.04 * g)
    P(bass(note(root), b * 3.9), t, 0.12 * g)
    up = 12 if q > 0.5 else 0
    for k in range(16):
        P(celesta(note(tones[k % 4] + up + (12 if k >= 8 else 0)), 0.5), t + k * b / 4, 0.06 * g)


def _comedy(P, t, b, ch, n, q):
    root, tones = ch
    P(tuba(note(root), b * 0.6), t, 0.3)
    P(tuba(note(root + 7 if root + 7 <= 47 else root - 5), b * 0.6), t + 2 * b, 0.27)
    for pos in (1, 3):
        for i in (0, 1, 2):
            P(pizz(note(tones[i])), t + pos * b, 0.07)
    for k, i in enumerate(R_COMEDY[n % 4]):
        if i is not None:
            P(square(note(tones[i] - 12), 0.18, 14), t + k * b / 2, 0.06)
            P(marimba(note(tones[i])), t + k * b / 2, 0.12)
    for k in range(4):
        P(wood(1300), t + k * b + b / 2, 0.05)


def _awkward(P, t, b, ch, n, q):
    """Bored-adult elevator music (the taxes class)."""
    root, tones = ch
    for tone in tones:
        P(epiano(note(tone), b * 3), t, 0.055)
    P(epiano(note(tones[2] + 12), b), t + 2.5 * b, 0.05)
    P(bass(note(root), b * 0.9), t, 0.15)
    P(bass(note(root + 7), b * 0.9), t + 2 * b, 0.12)
    for k in range(4):
        P(wood(2400, 0.04), t + k * b, 0.04)


def _sad(P, t, b, ch, n, q):
    root, tones = ch
    P(pad(note(tones[0] - 12), b * 4), t, 0.05)
    P(pad(note(tones[1] - 12), b * 4), t, 0.04)
    P(pad(note(root + 12), b * 4), t, 0.04)
    P(bass(note(root), b * 3.9), t, 0.12)
    mel = [[(0, 2), (2, 1)], [(0, 1), (2, 0)], [(0, 2), (1, 3), (2, 1)], [(0, 1), (3, 0)]]
    for pos, i in mel[n % 4]:
        P(epiano(note(tones[i]), 1.8), t + pos * b, 0.09)


def _low(P, t, b, ch, n, q):
    """The low point: a slow heartbeat under a dark pad."""
    root, tones = ch
    P(pad(note(tones[0] - 12), b * 4), t, 0.045)
    P(pad(note(root + 12), b * 4), t, 0.04)
    for pos in (0, 2):
        P(kick(), t + pos * b, 0.3)
        P(kick(), t + pos * b + 0.28, 0.2)
    if n % 2 == 0:
        P(celesta(note(tones[3] + 12), 2.0), t + b, 0.05)


def _chase(P, t, b, ch, n, q):
    root, tones = ch
    for k in range(8):
        P(bass(note(root + (12 if k % 4 == 2 else 0)), b * 0.4), t + k * b / 2, 0.19)
    for k in range(16):
        P(square(note(tones[[0, 1, 2, 1][k % 4]] + (12 if n % 2 else 0)), 0.1, 20), t + k * b / 4, 0.04)
    for k in range(4):
        P(kick(), t + k * b, 0.3)
        P(wood(1500), t + k * b + b / 2, 0.07)


def _villain(P, t, b, ch, n, q):
    """The admin: a low 'dun dun DUN' march."""
    root, tones = ch
    for pos, semi in ((0, 0), (0.75, 0), (1.5, 3), (2.5, 1), (3, 0)):
        P(tuba(note(root + semi), b * 0.5), t + pos * b, 0.3)
    for i in (0, 1, 2):
        P(brass(note(tones[i] - 12), b * 0.7, 3), t, 0.06)
    if n % 2 == 0:
        P(timp(note(root - 12)), t, 0.18)
    for pos in (0.5, 2):
        P(pizz(note(tones[0])), t + pos * b, 0.06)
    P(kick(), t, 0.25)
    P(kick(), t + 2 * b, 0.18)


def _sneaky(P, t, b, ch, n, q):
    """Tiptoe pizzicato (whispering in class)."""
    root, tones = ch
    for k, semi in enumerate((0, 3, 2, 1)):
        P(pizz(note(root + 12 + semi)), t + k * b, 0.16)
    hits = [(0.5, 2), (2.5, 1), (3.5, 3)] if n % 2 else [(0.5, 1), (1.5, 2), (3.5, 0)]
    for pos, i in hits:
        P(pizz(note(tones[i] + 12)), t + pos * b, 0.07)
    P(wood(1700, 0.05), t + 1.5 * b, 0.05)
    P(wood(1500, 0.05), t + 3.5 * b, 0.05)


def _spooky(P, t, b, ch, n, q):
    """Silly-spooky (the zombie lunch): a wobbly theremin over a walking pizzicato."""
    root, tones = ch
    for k, semi in enumerate((0, 7, 12, 7, 0, 7, 12, 7)):
        P(pizz(note(root + semi)), t + k * b / 2, 0.14)
    mel = [[(0, 2, 2), (2, 1, 2)], [(0, 3, 1.5), (1.5, 2, 2.5)]][n % 2]
    for pos, i, d in mel:
        P(theremin(note(tones[i]), b * d), t + pos * b, 0.09)
    P(wood(900), t + b, 0.06)
    P(wood(900), t + 3 * b, 0.06)
    if n % 2:
        P(celesta(note(tones[3] + 12), 1.0), t + 3.5 * b, 0.06)


def _romance(P, t, b, ch, n, q):
    """Cheesy waltz (the kiss emote), 3/4."""
    root, tones = ch
    P(bass(note(root), b * 0.9), t, 0.15)
    for pos in (1, 2):
        for i in (0, 1, 2):
            P(guitar(note(tones[i]), 0.6), t + pos * b, 0.05)
    mel = [[(0, 3, 2), (2, 2, 1)], [(0, 2, 3)], [(0, 3, 1), (1, 2, 1), (2, 1, 1)], [(0, 1, 3)]]
    for pos, i, d in mel[n % 4]:
        P(violin(note(tones[i]), b * d), t + pos * b, 0.075)
    P(pad(note(tones[0] - 12), b * 3), t, 0.03)


def _ominous(P, t, b, ch, n, q):
    root, tones = ch
    P(pad(note(root), b * 4), t, 0.06)
    P(pad(note(root - 12), b * 4), t, 0.06)
    P(pad(note(tones[1] - 12), b * 4), t, 0.03)
    P(kick(), t, 0.28)
    P(kick(), t + 0.3, 0.18)
    if n % 2:
        P(celesta(note(tones[3] + 12), 2.0), t + 2 * b, 0.05)
    if n % 4 == 0:
        P(timp(note(root - 12)), t, 0.12)


def _mystery(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 3.9), t, 0.12)
    P(pad(note(tones[0] - 12), b * 4), t, 0.035)
    for k, i in enumerate([0, 2, 1, 3, 2, 1, 3, 2]):
        if (k + n) % 3 != 2:
            P(celesta(note(tones[i]), 0.6), t + k * b / 2, 0.075)
    for k in range(4):
        P(wood(2600, 0.04), t + k * b, 0.05)


def _tension(P, t, b, ch, n, q):
    root, tones = ch
    g = 0.8 + 0.4 * q
    for k, semi in enumerate([0, 0, 3, 0, 1, 0, 3, 0] * 2):
        P(square(note(root + 12 + semi), 0.12, 16), t + k * b / 4, 0.045 * g)
    P(pad(note(tones[0] - 12), b * 4), t, 0.04 * g)
    P(pad(note(tones[1] - 12), b * 4), t, 0.035 * g)
    P(kick(), t, 0.22 * g)
    P(kick(), t + 2 * b, 0.18 * g)
    P(tom(110), t + 3.5 * b, 0.15 * g)


def _montage(P, t, b, ch, n, q):
    """Studying for the first time: a determined, hopeful build."""
    root, tones = ch
    for k in range(8):
        P(bass(note(root + (12 if k % 2 else 0)), b * 0.45), t + k * b / 2, 0.16)
    for k, i in enumerate([0, 1, 2, 1, 3, 1, 2, 1]):
        P(marimba(note(tones[i])), t + k * b / 2, 0.13)
    mel = [(0, 3, 1), (1, 2, 0.5), (1.5, 3, 1.5), (3, 1, 1)] if n % 2 == 0 else [(0, 2, 2), (2, 3, 2)]
    for pos, i, d in mel:
        P(square(note(tones[i] + 12), b * d, 3), t + pos * b, 0.05)
    for k in range(4):
        P(kick(), t + k * b, 0.28)
        P(wood(1500 if k % 2 else 1250), t + k * b + b / 2, 0.06)


def _cool(P, t, b, ch, n, q):
    """Priya, the level-99 pro: a laid-back G dorian groove with finger snaps."""
    root, tones = ch
    for pos in (0, 0.75, 2, 2.5, 3.5):
        P(bass(note(root + (12 if pos == 2.5 else 0)), b * 0.4), t + pos * b, 0.18)
    for pos in (0.5, 1.75, 3):
        for tone in tones[:3]:
            P(epiano(note(tone), b * 0.6), t + pos * b, 0.05)
    for k in (1, 3):
        P(wood(2200, 0.05), t + k * b, 0.08)
    P(kick(), t, 0.22)
    P(kick(), t + 2.5 * b, 0.15)


def _boss(P, t, b, ch, n, q):
    """The Final Exam: heavy, slow, low brass and timpani, a dark choir."""
    root, tones = ch
    P(pad(note(root + 12), b * 4), t, 0.07)
    for i in (0, 1, 2):
        P(pad(note(tones[i] - 12), b * 4), t, 0.045)
    P(timp(note(root - 12)), t, 0.25)
    P(timp(note(root - 12)), t + 2.5 * b, 0.2)
    for pos in (0, 0.75, 2.5):
        for i in (0, 1, 2):
            P(brass(note(tones[i] - 12), b * 0.5, 3), t + pos * b, 0.07)
    P(bass(note(root), b * 1.8), t, 0.22)
    P(bass(note(root), b * 1.3), t + 2.5 * b, 0.2)
    P(kick(), t, 0.32)
    P(kick(), t + 2 * b, 0.32)


def _battle(P, t, b, ch, n, q, tick=False):
    root, tones = ch
    for k in range(8):
        P(bass(note(root), b * 0.42), t + k * b / 2, 0.2)
    for pos in (0, 1.5, 3):
        for i in (0, 1, 2):
            P(brass(note(tones[i] - 12), b * 0.6, 4), t + pos * b, 0.06)
    if n % 2:
        for k in range(16):
            P(square(note(tones[k % 4] + (12 if k >= 8 else 0)), 0.12, 18), t + k * b / 4, 0.045)
    for k in range(4):
        P(kick(), t + k * b, 0.3)
    P(tom(130), t + 3.5 * b, 0.22)
    P(tom(98), t + 3.75 * b, 0.22)
    if tick:                                                    # the countdown clock
        for k in range(4):
            P(wood(2600, 0.05), t + k * b, 0.1)


def _countdown(P, t, b, ch, n, q):
    _battle(P, t, b, ch, n, q, tick=True)


def _heroic(P, t, b, ch, n, q):
    root, tones = ch
    for k in range(8):
        P(bass(note(root + (7 if k in (3, 7) else 0)), b * 0.45), t + k * b / 2, 0.18)
    P(pad(note(tones[0] - 12), b * 4), t, 0.05)
    P(pad(note(tones[2] - 12), b * 4), t, 0.04)
    mel = [(0, 3, 1.5), (1.5, 2, 0.5), (2, 1, 2)] if n % 2 == 0 else [(0, 2, 1), (1, 3, 1), (2, 3, 2)]
    for pos, i, d in mel:
        P(brass(note(tones[i]), b * d, 1.2), t + pos * b, 0.08)
    for k in range(4):
        P(kick(), t + k * b, 0.28)
        P(wood(1500), t + k * b + b / 2, 0.06)
    if n % 4 == 3:
        for pos, f in ((3, 130), (3.5, 110), (3.75, 90)):
            P(tom(f), t + pos * b, 0.2)


def _final(P, t, b, ch, n, q):
    """The last 10 seconds: the heroic theme, faster, with a running celesta."""
    _heroic(P, t, b, ch, n, q)
    root, tones = ch
    for k in range(16):
        P(celesta(note(tones[k % 4] + 12), 0.3), t + k * b / 4, 0.05)


def _triumph(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 1.9), t, 0.2)
    P(bass(note(root + 7), b * 1.9), t + 2 * b, 0.14)
    fan = [[(0, 0, 0.5), (0.5, 1, 0.5), (1, 2, 1), (2, 3, 2)], [(0, 3, 1), (1, 2, 1), (2, 3, 2)]][n % 2]
    for pos, i, d in fan:
        P(brass(note(tones[i]), b * d, 1.0), t + pos * b, 0.085)
    for k in range(8):
        P(marimba(note(tones[k % 4])), t + k * b / 2, 0.14)
    for k in (0, 2):
        P(kick(), t + k * b, 0.3)
    for k in range(4):
        P(wood(1500 if k % 2 else 1250), t + k * b + b / 2, 0.07)


def _warm(P, t, b, ch, n, q):
    root, tones = ch
    P(bass(note(root), b * 3.8), t, 0.17)
    P(pad(note(tones[0] - 12), b * 4), t, 0.035)
    P(pad(note(tones[1] - 12), b * 4), t, 0.03)
    for k, i in enumerate([0, 1, 2, 1, 3, 1, 2, 1]):
        if (k + n) % 5 != 4:
            P(guitar(note(tones[i])), t + k * b / 2, 0.13)
    P(kick(), t, 0.15)


def _drone(P, t, b, ch, n, q):
    root, tones = ch
    P(pad(note(root), b * 4), t, 0.05)
    P(pad(note(root + 7), b * 4), t, 0.04)


def _p(*names):
    return [CH[x] for x in names]


# name: bar function, bpm, beats per bar, progression, level offset in dB (after normalising to LEVEL)
MOODS = dict(
    hype=dict(fn=_hype, bpm=136, beats=4, prog=_p("G", "Gm", "Eb", "D7"), db=0.0),
    game=dict(fn=_game, bpm=128, beats=4, prog=_p("G", "Gm", "Eb", "D7"), db=-1.0),
    wonder=dict(fn=_wonder, bpm=108, beats=4, prog=_p("G", "DF", "Em", "C"), db=-1.0),
    night=dict(fn=_night, bpm=76, beats=4, prog=_p("Gm", "Eb", "Cm", "D"), db=-4.5),
    magic=dict(fn=_magic, bpm=120, beats=4, prog=_p("Gm", "Eb", "Cm", "D"), db=-1.5),
    comedy=dict(fn=_comedy, bpm=116, beats=4, prog=_p("G", "C", "D7", "G"), db=-1.0),
    awkward=dict(fn=_awkward, bpm=70, beats=4, prog=_p("Gmaj7", "Cmaj7", "Am7", "D9"), db=-3.5),
    sad=dict(fn=_sad, bpm=66, beats=4, prog=_p("Gm", "Eb", "Bb", "D"), db=-4.0),
    low=dict(fn=_low, bpm=60, beats=4, prog=_p("Gm", "Cm", "Gm", "D"), db=-4.0),
    chase=dict(fn=_chase, bpm=156, beats=4, prog=_p("Gm", "Gm", "Eb", "D"), db=0.0),
    villain=dict(fn=_villain, bpm=96, beats=4, prog=_p("Gm", "Gm", "Eb", "D"), db=-1.5),
    sneaky=dict(fn=_sneaky, bpm=100, beats=4, prog=_p("Gm", "Gm", "Cm", "D"), db=-2.5),
    spooky=dict(fn=_spooky, bpm=108, beats=4, prog=_p("Gm", "Eb", "Gm", "D7"), db=-1.5),
    romance=dict(fn=_romance, bpm=84, beats=3, prog=_p("G", "Em", "C", "D"), db=-1.5),
    ominous=dict(fn=_ominous, bpm=58, beats=4, prog=_p("Gm", "Ab", "Gm", "Ab"), db=-3.0),
    mystery=dict(fn=_mystery, bpm=92, beats=4, prog=_p("Gm", "Eb", "Cm", "D"), db=-3.0),
    tension=dict(fn=_tension, bpm=112, beats=4, prog=_p("Gm", "Gm", "Eb", "D"), db=-2.0),
    montage=dict(fn=_montage, bpm=124, beats=4, prog=_p("G", "Bm", "C", "D"), db=-0.5),
    cool=dict(fn=_cool, bpm=96, beats=4, prog=_p("Gm7", "C7", "Gm7", "C7"), db=-2.0),
    boss=dict(fn=_boss, bpm=84, beats=4, prog=_p("Gm", "Ab", "Gm", "D"), db=1.0),
    battle=dict(fn=_battle, bpm=150, beats=4, prog=_p("Gm", "Eb", "F", "D"), db=0.5),
    countdown=dict(fn=_countdown, bpm=150, beats=4, prog=_p("Gm", "Eb", "F", "D"), db=0.5),
    heroic=dict(fn=_heroic, bpm=140, beats=4, prog=_p("G", "Eb", "F", "G"), db=0.5),
    final=dict(fn=_final, bpm=164, beats=4, prog=_p("G", "Eb", "F", "D"), db=1.0),
    triumph=dict(fn=_triumph, bpm=128, beats=4, prog=_p("G", "C", "D", "G"), db=0.5),
    warm=dict(fn=_warm, bpm=92, beats=4, prog=_p("G", "Em", "C", "D"), db=-2.5),
    drone=dict(fn=_drone, bpm=60, beats=4, prog=_p("G", "G", "Gm", "G"), db=-11.0),
)


def _render(mood, play, tail=0.5):
    """`play` seconds of a mood from its own downbeat; notes that start later are left out, the ones playing at the
    end ring for `tail` seconds and fade."""
    m = MOODS[mood]
    b = 60.0 / m["bpm"]
    bar_len = b * m["beats"]
    out = np.zeros(int(SR * (play + tail + 6)))

    def P(x, at, g):
        if at >= play - 1e-6 or g <= 0:
            return
        s = int(round(at * SR))
        e = min(len(out), s + len(x))
        out[s:e] += x[:e - s] * g

    t, n = 0.0, 0
    while t < play:
        m["fn"](P, t, b, m["prog"][n % len(m["prog"])], n, min(1.0, t / max(play, 1e-6)))
        t += bar_len
        n += 1
    out = out[:int(SR * (play + tail))]
    g = np.ones_like(out)
    i0 = int(SR * play)
    g[i0:] = np.linspace(1, 0, len(g[i0:])) ** 2
    nf = int(SR * 0.012)
    g[:nf] *= np.linspace(0, 1, nf)
    return out * g


_NORM = {}


def norm(mood):
    """Gain that brings a mood to LEVEL * 10^(db/20) (measured on 16 s of it)."""
    if mood not in _NORM:
        x = _render(mood, 16.0, 0.0)
        _NORM[mood] = LEVEL / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 10 ** (MOODS[mood]["db"] / 20)
    return _NORM[mood]


# ---------- stings ----------
def _st_hit(major=False):
    tones = (43, 55, 59 if major else 58, 62, 67)
    x = sum(brass(note(m), 2.2, 1.6) for m in tones) * 0.5
    x += timp(note(31), 2.2) * 0.9
    x += sum(pad(note(m), 2.2, 0.02) for m in (55, 62)) * 0.3
    return x


def _st_rise(d=2.5):
    t = tt(d)
    f = note(55) * 2 ** (2 * t / d)                          # G3 up two octaves
    ph = TWO_PI * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * (t / d) ** 2
    x += sum(pad(note(m), d, d * 0.8) for m in (55, 62, 67)) * 0.25 * (t / d)
    return x * _rel(t, d, 0.03)


def _st_drop(d=1.0):
    """Power-down / tape stop (the lights go out, 'let me explain')."""
    t = tt(d)
    f = note(67) * 2 ** (-2.5 * t / d)
    ph = TWO_PI * np.cumsum(f) / SR
    x = sum(np.sin(h * ph) / h for h in (1, 3, 5))
    return x * _att(t, 0.01) * np.exp(-t * 2.5) * _rel(t, d, 0.1)


def _st_fail():
    """Sad trombone: three falling notes and a long wobbly one."""
    out = np.zeros(int(SR * 2.4))
    at = 0.0
    for m, d in ((58, 0.38), (57, 0.38), (56, 0.38), (55, 1.2)):
        t = tt(d)
        ph = _phase(note(m), t, 6.0, 0.02 if d > 1 else 0.0)
        x = sum(np.sin(h * ph) / h * (1.0 if h <= 2 else np.exp(-t * h * 0.6)) for h in range(1, 7))
        x = x * _att(t, 0.03) * _rel(t, d, 0.08)
        s = int(at * SR)
        out[s:s + len(x)] += x
        at += d
    return out


def _st_fanfare():
    """'ta-ta-ta-taaa' in G major."""
    out = np.zeros(int(SR * 2.0))
    for at, ms, d in ((0.0, (67,), 0.12), (0.14, (67,), 0.12), (0.28, (67,), 0.12),
                      (0.42, (55, 62, 67, 71, 74), 1.4)):
        x = sum(brass(note(m), d, 1.4) for m in ms)
        s = int(at * SR)
        out[s:s + len(x)] += x
    return out


def _st_sparkle():
    out = np.zeros(int(SR * 1.6))
    for k, m in enumerate((79, 83, 86, 91, 95)):
        x = celesta(note(m), 1.2)
        s = int(k * 0.06 * SR)
        out[s:s + len(x)] += x
    return out


STINGS_FN = dict(hit=_st_hit, hit_major=lambda: _st_hit(True), rise=_st_rise, drop=_st_drop, fail=_st_fail,
                 fanfare=_st_fanfare, sparkle=_st_sparkle)
STING_DB = dict(hit=6.0, hit_major=6.0, rise=3.0, drop=2.0, fail=2.0, fanfare=4.0, sparkle=0.0)


def sting(kind):
    x = STINGS_FN[kind]()
    w = int(SR * 0.5)                                          # level of its loudest half second
    e = np.convolve(x ** 2, np.ones(w) / w, mode="valid")
    r = np.sqrt(e.max()) + 1e-9
    return x / r * LEVEL * 10 ** (STING_DB[kind] / 20)


# ---------- the score ----------
def music_score(total, cues, stings=(), tail=0.5, end_fade=0.25):
    """cues = [(t, mood), ...] sorted, the first at 0; stings = [(t, kind), ...] ("rise" ENDS at t)."""
    out = np.zeros(int(SR * (total + 6)))

    def put(x, at):
        s = int(round(at * SR))
        if s < 0:
            x, s = x[-s:], 0
        e = min(len(out), s + len(x))
        if s < len(out):
            out[s:e] += x[:e - s]

    for i, (t0, mood) in enumerate(cues):
        t1 = cues[i + 1][0] if i + 1 < len(cues) else total
        put(_render(mood, t1 - t0, tail) * norm(mood), t0)
    for t, kind in stings:
        x = sting(kind)
        put(x, t - len(x) / SR if kind == "rise" else t)
    out = out[:int(SR * total)]
    n = int(SR * end_fade)
    out[-n:] *= np.linspace(1, 0, n)
    peak = np.max(np.abs(out))
    if peak > 0.95:                                           # soft limit the rare peaks, keep the level
        k = np.abs(out) > 0.8
        out[k] = np.sign(out[k]) * (0.8 + 0.15 * np.tanh((np.abs(out[k]) - 0.8) / 0.15))
    return out


def save_raw(path, x):
    """Write a stereo 16-bit wav WITHOUT normalising (audio.save normalises the peak, which would move the level)."""
    x = np.clip(np.asarray(x, np.float32), -1, 1)
    x = np.stack([x, x], 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def mood_at(cues, t):
    m = cues[0][1]
    for t0, mood in cues:
        if t0 <= t:
            m = mood
    return m


if __name__ == "__main__":
    if sys.argv[1] == "--demo":
        d = sys.argv[2]
        os.makedirs(d, exist_ok=True)
        for name in MOODS:
            save_raw(os.path.join(d, f"mood_{name}.wav"), _render(name, 8.0) * norm(name))
        for name in STINGS_FN:
            save_raw(os.path.join(d, f"sting_{name}.wav"), sting(name))
        print("wrote", len(MOODS), "moods and", len(STINGS_FN), "stings to", d)
    else:
        import importlib
        story = importlib.import_module(sys.argv[1])
        x = music_score(story.TOTAL, story.SCORE, getattr(story, "STINGS", ()))
        save_raw(sys.argv[2], x)
        print(f"wrote {sys.argv[2]}: {len(x) / SR:.1f} s, {len(story.SCORE)} music cues, "
              f"{len(getattr(story, 'STINGS', ()))} stings, rms {np.sqrt(np.mean(x ** 2)):.4f}, "
              f"peak {np.max(np.abs(x)):.3f}")
