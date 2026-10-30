"""Synthesised SFX and a light background music bed (no third-party samples)."""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
rng = np.random.default_rng(1)


def save(path, x):
    x = np.asarray(x, np.float32)
    peak = np.max(np.abs(x)) or 1.0
    x = x / peak * 0.9
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def tt(d):
    return np.arange(int(SR * d)) / SR


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def onepole(x, cutoff):
    """Vectorised-enough one-pole low-pass via cumulative filtering in blocks."""
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    return lowpass(x, a)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * decay)


def whoosh():
    t = tt(0.55)
    n = rng.standard_normal(len(t))
    sweep = onepole(n, 2500) - onepole(n, 300)
    e = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 2
    return sweep * e


def tick():
    t = tt(0.06)
    return (np.sin(2 * np.pi * 3200 * t) * 0.6 + rng.standard_normal(len(t)) * 0.4) * np.exp(-t * 120)


def bell():
    t = tt(3.5)
    f = 196
    parts = [(0.5, 1.0, 0.6), (1.0, 1.0, 1.0), (1.19, 0.5, 1.3), (1.5, 0.45, 1.6),
             (2.0, 0.35, 2.0), (2.52, 0.2, 2.6), (3.0, 0.12, 3.2)]
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in parts)
    return x * np.minimum(1, t / 0.004)


def pop():
    t = tt(0.14)
    f = 900 * np.exp(-t * 18) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)


def thud():
    t = tt(0.35)
    f = 120 * np.exp(-t * 10) + 45
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    return x + onepole(rng.standard_normal(len(t)), 400) * np.exp(-t * 40) * 2


def sparkle():
    out = np.zeros(int(SR * 0.9))
    for k, f in enumerate((1760, 2217, 2637, 3520)):
        t = tt(0.5)
        s = int(k * 0.07 * SR)
        out[s:s + len(t)] += np.sin(2 * np.pi * f * t) * np.exp(-t * 9)
    return out


def coin():
    t = tt(0.35)
    return (np.sin(2 * np.pi * 2490 * t) + 0.6 * np.sin(2 * np.pi * 3320 * t)) * np.exp(-t * 14)


def page():
    t = tt(0.18)
    n = rng.standard_normal(len(t))
    return (n - onepole(n, 1500)) * np.sin(np.pi * t / 0.18) ** 2


def boing():
    t = tt(0.8)
    f = 180 + 120 * np.sin(2 * np.pi * 7 * t) * np.exp(-t * 3) + 150 * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)


def step():
    t = tt(0.16)
    return onepole(rng.standard_normal(len(t)), 600) * np.exp(-t * 35) * 3


def murmur():
    t = tt(2.2)
    n = onepole(rng.standard_normal(len(t)), 500)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 3.3 * t) * np.sin(2 * np.pi * 1.7 * t)
    return n * am * np.sin(np.pi * t / 2.2)


def chord_hit(freqs, d, decay, bright=6):
    t = tt(d)
    x = np.zeros(len(t))
    for f in freqs:
        for h in range(1, bright + 1):
            x += np.sin(2 * np.pi * f * h * t) / h
    return x * env(len(t), 0.01, decay)


def sting():
    return chord_hit((110, 130.8, 155.6), 1.6, 2.2) + chord_hit((55,), 1.6, 2.5, 3) * 0.8


def sting_soft():
    return chord_hit((220, 261.6, 311.1), 1.2, 3.0, 3) * 0.6


def sting_low():
    t = tt(2.4)
    return chord_hit((41.2, 61.7, 87.3), 2.4, 1.4, 5) + np.sin(2 * np.pi * 30 * t) * np.exp(-t * 1.5)


# ---------- Style B SFX (punchier game sounds, sound_design.md section 2) ----------
def swish():
    t = tt(0.16)
    n = rng.standard_normal(len(t))
    hi = n - onepole(n, 1800)
    return hi * np.sin(np.pi * t / 0.16) ** 2 * (0.4 + t / 0.16)


def hit():
    """Deep punchy low hit (Style B 'thud' family: >45% of the energy under 200 Hz)."""
    t = tt(0.4)
    f = 140 * np.exp(-t * 14) + 50
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.6
    x += 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    return x + onepole(rng.standard_normal(len(t)), 250) * np.exp(-t * 45) * 1.0


def click():
    t = tt(0.035)
    return (np.sin(2 * np.pi * 1800 * t) + rng.standard_normal(len(t)) * 0.5) * np.exp(-t * 180)


def boom():
    t = tt(0.7)
    f = 90 * np.exp(-t * 7) + 38
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 1.6
    x += 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return x + onepole(rng.standard_normal(len(t)), 250) * np.exp(-t * 30) * 1.2


def ding():
    t = tt(1.4)
    f = 1568   # G6
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in
            ((1, 1.0, 3.0), (2.0, 0.4, 5.0), (2.76, 0.25, 7.0), (5.4, 0.1, 9.0)))
    return x * np.minimum(1, t / 0.002)


def chaching():
    out = np.zeros(int(SR * 1.2))
    c = click()
    out[:len(c)] += c * 0.8
    k = coin()
    s = int(0.08 * SR)
    out[s:s + len(k)] += k
    d = ding()
    s = int(0.16 * SR)
    out[s:s + len(d[:len(out) - s])] += d[:len(out) - s] * 0.8
    return out


def whip():
    t = tt(0.3)
    n = rng.standard_normal(len(t))
    band = onepole(n, 4000) - onepole(n, 600)
    return band * np.sin(np.pi * np.clip(t / 0.3, 0, 1)) ** 3


def type_key():
    t = tt(0.05)
    return (np.sin(2 * np.pi * 2400 * t) * 0.4 + rng.standard_normal(len(t)) * 0.6) * np.exp(-t * 140)


def buzz():
    """'Wrong' error buzzer."""
    t = tt(0.45)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.5
    return onepole(x, 2500) * np.minimum(1, t / 0.01) * np.minimum(1, (0.45 - t) / 0.05)


def success():
    """Rising three-note 'access granted' chime (G major arpeggio)."""
    out = np.zeros(int(SR * 1.0))
    for k, f in enumerate((784, 988, 1175, 1568)):
        t = tt(0.6)
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 6)
        s = int(k * 0.07 * SR)
        out[s:s + len(t)] += x[:len(out) - s]
    return out


# ---------- music ----------
def pluck(f, d, bright=5, decay=6.0):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (decay + h * 2.5)) / h for h in range(1, bright + 1))
    return x * np.minimum(1, t / 0.003)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def music_ref(total, swell_at=None):
    """Background bed measured on the 3 references (sound_design.md): minor key (D minor),
    ~96 bpm, soft mid-range plucks over a warm bass, ~2 notes/s, almost no drums,
    a swell under the last line. Mix it ~21 dB under the voice."""
    out = np.zeros(int(SR * (total + 3)))
    beat = 60 / 96

    def put(x, at):
        s = int(at * SR)
        e = min(len(out), s + len(x))
        if s < len(out):
            out[s:e] += x[:e - s]

    prog = [(38, [62, 65, 69]), (34, [58, 62, 65]), (41, [60, 65, 69]), (33, [61, 64, 69])]  # Dm Bb F A
    pattern = [0, 2, 1, 2, 0, 1, 2, 1]                                                       # 2 notes per beat
    t, bar = 0.0, 0
    while t < total:
        root, tones = prog[bar % 4]
        tb = tt(beat * 4.3)   # sustained warm bass (a pluck's fundamental dies within the bar)
        b = (np.sin(2 * np.pi * note(root) * tb) * 0.07 + np.sin(2 * np.pi * note(root + 12) * tb) * 0.03) \
            * np.exp(-tb * 0.25)
        k = np.arange(len(b))
        b *= np.minimum(1, k / (SR * 0.08)) * np.minimum(1, (len(b) - k) / (SR * 0.25))  # soft in, no click out
        put(b, t)
        for k, i in enumerate(pattern):
            if (k + bar) % 3 == 2:          # leave gaps: sparse, not a wall of notes
                continue
            m = pluck(note(tones[i]), 0.9, 3, 5) * 0.33
            put(m * np.minimum(1, (len(m) - np.arange(len(m))) / (SR * 0.1)), t + k * beat / 2)
        t += beat * 4
        bar += 1
    if swell_at is not None:
        n = int(SR * max(0.5, total - swell_at))
        sw = sum(np.sin(2 * np.pi * note(m) * np.arange(n) / SR) for m in (50, 57, 62, 65)) * 0.12
        put(sw * np.linspace(0, 1, n) ** 2, swell_at)
    put(sum(pluck(note(m), 3.0, 3, 1.2) for m in (38, 50, 57, 62, 65)) * 0.5, total - 2.8)
    out = out[:int(SR * total)]
    n = int(SR * 1.2)
    out[-n:] *= np.linspace(1, 0, n)
    return out


def music(total, sad_from, sad_to):
    out = np.zeros(int(SR * (total + 3)))
    bpm = 104
    beat = 60 / bpm

    def put(x, at):
        s = int(at * SR)
        e = min(len(out), s + len(x))
        if s < len(out):
            out[s:e] += x[:e - s]

    major = [(48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (43, [55, 59, 62, 67])]
    minor = [(45, [57, 60, 64]), (41, [57, 60, 65]), (40, [56, 59, 64]), (45, [57, 60, 64])]
    t = 0.0
    bar = 0
    while t < total:
        sad = sad_from <= t < sad_to
        prog = minor if sad else major
        root, tones = prog[bar % 4]
        put(pluck(note(root - 12 if sad else root), beat * 3.5, 3, 2.5) * 0.9, t)
        steps = 4 if sad else 8
        for k in range(steps):
            at = t + k * (beat * 4 / steps)
            m = tones[(k * (2 if sad else 1)) % len(tones)]
            if not sad and k % 4 == 3:
                m += 12
            put(pluck(note(m), 0.6, 5, 9 if not sad else 4) * (0.35 if sad else 0.42), at)
        if not sad:
            for k in range(4):
                n = rng.standard_normal(int(SR * 0.05))
                put((n - onepole(n, 5000)) * np.exp(-np.arange(len(n)) / SR * 80) * 0.15, t + k * beat + beat / 2)
        t += beat * 4
        bar += 1
    put(sum(pluck(note(m), 3.0, 4, 1.2) for m in (48, 55, 60, 64)) * 0.5, total - 2.8)
    out = out[:int(SR * total)]
    fade = np.ones_like(out)
    n = int(SR * 1.2)
    fade[-n:] = np.linspace(1, 0, n)
    return out * fade


def music_game(total, start=0.0, dips=(), bpm=120, end_hit=True):
    """Style B bed (sound_design.md section 1): cheeky game tune centred on G that swings
    between major and minor (G | Gm | Eb | D7), a soft root-fifth bass, a marimba + square
    lead; ~2 notes/s. All attacks are >= 8 ms and there are no noise hats, so
    analysis/audio_ref.py does not count the music as SFX. `start` fades the bed in (the references often start it after the
    hook); `dips` = [(t0, t1), ...] drop it ~9 dB (slow-motion / dramatic beats).
    Mix with assemble.py --music-volume MUSIC_VOL (about -10 dB under the voice, measured)."""
    out = np.zeros(int(SR * (total + 3)))
    beat = 60 / bpm

    def put(x, at):
        s = int(at * SR)
        e = min(len(out), s + len(x))
        if 0 <= s < len(out):
            out[s:e] += x[:e - s]

    def square(f, d, decay, att=0.008):
        t = tt(d)
        x = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 3, 5, 7, 9))
        return x * np.minimum(1, t / att) * np.exp(-t * decay)

    def marimba(f, d=0.5):
        t = tt(d)
        return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) \
            * np.exp(-t * 9) * np.minimum(1, t / 0.008)

    def bass(f, d):
        t = tt(d)
        x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
        return x * np.minimum(1, t / 0.07) * np.exp(-t * 1.5) * np.minimum(1, (d - t) / 0.05)

    # (bass root, chord tones for the lead) per bar: G | Gm | Eb | D7, a cheeky major/minor swing on G
    prog = [(43, [67, 71, 74, 79]), (43, [67, 70, 74, 79]), (39, [67, 70, 75, 79]), (38, [66, 69, 72, 74])]
    riffs = [[0, None, 2, None, None, None, None, None], [None, None, None, 2, 1, None, None, None],
             [0, None, None, None, None, 3, None, None], [3, None, None, None, 1, None, None, None]]
    t, bar = 0.0, 0
    while t < total:
        root, tones = prog[bar % 4]
        put(bass(note(root), beat * 1.9) * 0.2, t)
        put(bass(note(root + 7), beat * 1.9) * 0.13, t + beat * 2)
        riff = riffs[(bar // 4 + bar) % 4]
        for k, i in enumerate(riff):
            if i is not None:
                put(marimba(note(tones[i])) * 0.3, t + k * beat / 2)
                put(square(note(tones[i] + 12), 0.3, 9) * 0.07, t + k * beat / 2)
        t += beat * 4
        bar += 1
    if end_hit:
        put(sum(square(note(m), 1.2, 3) for m in (43, 55, 59, 62, 67)) * 0.25, total - 1.0)
    out = out[:int(SR * total)]
    gain = np.ones_like(out)
    if start > 0:
        n0 = int(SR * start)
        gain[:n0] = 0.0
        gain[n0:n0 + int(SR * 0.6)] = np.linspace(0, 1, len(gain[n0:n0 + int(SR * 0.6)]))
    for a, b in dips:
        i0, i1 = int(SR * a), int(SR * b)
        r = int(SR * 0.15)
        seg = np.full(max(0, i1 - i0), 0.35)
        seg[:r] = np.linspace(1, 0.35, len(seg[:r]))
        seg[-r:] = np.linspace(0.35, 1, len(seg[-r:]))
        gain[i0:i1] *= seg[:len(gain[i0:i1])]
    n = int(SR * 0.4)
    gain[-n:] *= np.linspace(1, 0, n)
    return out * gain


SFX_FUNCS = dict(whoosh=whoosh, tick=tick, bell=bell, pop=pop, thud=thud, sparkle=sparkle, coin=coin,
                 page=page, boing=boing, step=step, murmur=murmur, sting=sting, sting_soft=sting_soft,
                 sting_low=sting_low, swish=swish, hit=hit, click=click, boom=boom, ding=ding, chaching=chaching,
                 whip=whip, type_key=type_key, buzz=buzz, success=success)

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in SFX_FUNCS.items():
        save(out / f"{name}.wav", fn())
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    save(out / "music.wav", music(total, 40.9, 51.05))
    save(out / "music_ref.wav", music_ref(total, swell_at=total - 4))
    save(out / "music_game.wav", music_game(total))
    print("wrote sfx + music to", out)
