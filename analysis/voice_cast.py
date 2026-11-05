#!/usr/bin/env python3
"""Cast sheet for a voice + SRT: how many characters speak, who says which line, and with what tone.

  python3 analysis/voice_cast.py <voice audio or video> <subs.srt> <out_dir> [--speakers N] [--separate]

  --speakers N  force the number of voices (otherwise chosen by silhouette, 1-8)
  --separate    the input still has music / SFX (a finished video): split the voice out first with
                analysis/separate.py (UVR model in analysis/models)
  --roles F     a JSON list [[t0, t1, "Speaker"], ...] (seconds) of hand-checked speakers: every sentence whose middle
                falls inside a range gets that speaker, all others are Narrator (use it after reading the story)

How it works (offline, no neural models):
1. The SRT text is cut into sentences (a speaker change almost always falls on a sentence end). Each sentence
   gets its time from its cue; a sentence boundary inside a cue is moved to the quietest point near it.
2. Per sentence: pitch (pyin median and p10-p90 range in semitones, the end contour), loudness, speed
   (words/s), breathiness (unvoiced share) and timbre (MFCC means over the voiced frames).
3. Voices: the sentences of 0.6 s or more are clustered by timbre + pitch (agglomerative); short ones join
   the nearest voice. The voice with the most talk time that says the hook / chapter lines is the Narrator.
   The others get a role GUESS from their pitch (kid > 290 Hz, woman 165-290, man < 165) and their words
   ("sweetie" -> Mom, "Mom," -> Kid ...).
4. Tone: each sentence is compared with its own speaker's average (z-scores) and with text cues, and mapped to
   the emotion tags of script_guide.md section 4.
Writes out_dir/cast.md (summary, voices, every line with its numbers), cast.json and script.txt (the user's
script format: `Speaker: [emotion] text [break] ...`). The guesses are a first draft: check the lines with a
low speaker confidence by ear."""
import json
import re
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt  # noqa: E402

SR, HOP = 16000, 160                       # 10 ms frames
ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------- audio
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def separate(path, out):
    prefix = str(Path(out) / "sep")
    voice = prefix + "_voice.wav"
    if not Path(voice).exists():
        subprocess.run([sys.executable, str(ROOT / "separate.py"), str(path),
                        str(ROOT / "models" / "UVR-MDX-NET-Inst_HQ_3.onnx"), prefix], check=True)
    return voice


def frames(y):
    rms = librosa.feature.rms(y=y, frame_length=640, hop_length=HOP, center=True)[0]
    db = 20 * np.log10(rms + 1e-6)
    f0, voiced, _ = librosa.pyin(y, fmin=70, fmax=900, sr=SR, frame_length=1024, hop_length=HOP)
    mf = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, n_fft=512, hop_length=HOP)
    n = min(len(db), len(f0), mf.shape[1])
    mf = mf[:, :n]
    loud = db[:n] > np.percentile(db[:n], 95) - 30
    mu, sd = mf[:, loud].mean(1, keepdims=True), mf[:, loud].std(1, keepdims=True) + 1e-6
    return dict(db=db[:n], f0=f0[:n], voiced=voiced[:n] & loud, loud=loud, mfcc=((mf - mu) / sd).T)


# ---------------------------------------------------------------- text -> timed sentences
SENT = re.compile(r"[^.?!…]+(?:[.?!…]+[\"')\]]*|$)")
ABBR = re.compile(r"\b(a\.m\.|p\.m\.|mr\.|mrs\.|ms\.|dr\.|st\.|vs\.|e\.g\.|i\.e\.|u\.s\.)", re.I)
DOT = "\u2024"                                  # a dot that does not end a sentence


def sentences(cues, fr):
    """[(start, end, text)] sentence by sentence; a sentence that runs over several cues is joined."""
    pieces = []                                   # (start, end, text, ends_sentence)
    db = np.convolve(fr["db"], np.ones(9) / 9, mode="same")
    for a, b, text in cues:
        text = ABBR.sub(lambda m: m.group(0).replace(".", DOT), text)
        parts = [p.strip().replace(DOT, ".") for p in SENT.findall(text) if p.strip()]
        if not parts:
            continue
        total = sum(len(p) for p in parts)
        t, out = a, []
        for i, p in enumerate(parts):
            if i == len(parts) - 1:
                e = b
            else:
                guess = t + (b - a) * len(p) / total
                lo, hi = int(max(t + 0.15, guess - 0.35) * 100), int(min(b - 0.15, guess + 0.35) * 100)
                e = (lo + int(np.argmin(db[lo:hi]))) / 100 if hi > lo else guess
            out.append((t, e, p, bool(re.search(r"[.?!…][\"')\]]*$", p))))
            t = e
        pieces += out
    sents, cur = [], None
    for a, b, p, done in pieces:
        if cur is not None and (a - cur[1] >= 0.35 or b - cur[0] > 8.0):   # no punctuation: a pause ends it
            sents.append(tuple(cur))
            cur = None
        cur = [a, b, p] if cur is None else [cur[0], b, cur[2] + " " + p]
        if done:
            sents.append(tuple(cur))
            cur = None
    if cur:
        sents.append(tuple(cur))
    return sents


# ---------------------------------------------------------------- features
def features(seg, fr):
    a, b, text = seg
    i, j = int(a * 100), max(int(a * 100) + 2, int(b * 100))
    v = fr["voiced"][i:j]
    l = fr["loud"][i:j]
    f0 = fr["f0"][i:j][v]
    f0 = f0[np.isfinite(f0)]
    words = len(re.findall(r"[\w'%]+", text))
    speech = max(0.2, l.sum() / 100)
    d = dict(start=round(a, 2), end=round(b, 2), text=text, words=words, dur=round(b - a, 2),
             db=round(float(np.percentile(fr["db"][i:j], 90)), 1) if j > i else -60.0,
             rate=round(words / speech, 2), unvoiced=round(1 - (v.sum() / max(1, l.sum())), 2))
    if len(f0) >= 5:
        st = 12 * np.log2(f0 / 100)
        tail = st[-max(3, len(st) // 4):]
        head = st[:max(3, len(st) // 4)]
        d.update(hz=round(float(np.median(f0)), 0), range_st=round(float(np.percentile(st, 90) - np.percentile(st, 10)), 1),
                 end_slope=round(float(np.median(tail) - np.median(head)), 1))
    else:
        d.update(hz=None, range_st=0.0, end_slope=0.0)
    m = fr["mfcc"][i:j][v if v.sum() >= 5 else l]
    d["_mfcc"] = m.mean(0) if len(m) else np.zeros(fr["mfcc"].shape[1])
    return d


# ---------------------------------------------------------------- speakers
def cluster(segs, k=None):
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    X = []
    for s in segs:
        hz = s["hz"] or 200.0
        X.append(np.concatenate([s["_mfcc"][1:13], [2.0 * np.log2(hz / 200.0)]]))
    X = np.array(X)
    X = (X - X.mean(0)) / (X.std(0) + 1e-6)
    long_ = np.array([s["dur"] >= 0.6 and s["hz"] is not None for s in segs])
    if long_.sum() < 4:
        long_[:] = True
    XL = X[long_]
    best, labels_l = None, np.zeros(len(XL), int)
    ks = [k] if k else range(2, min(8, len(XL) - 1) + 1)
    for n in ks:
        lab = AgglomerativeClustering(n_clusters=n, linkage="ward").fit_predict(XL)
        if len(set(lab)) < 2:
            continue
        sc = silhouette_score(XL, lab)
        if k or best is None or sc > best + 0.01:     # prefer fewer voices unless clearly better
            best, labels_l = sc, lab
    if not k and (best is None or best < 0.08):       # no clear structure: one voice
        labels_l[:] = 0
        best = best or 0.0
    cents = np.array([XL[labels_l == c].mean(0) for c in sorted(set(labels_l))])
    dist = np.linalg.norm(X[:, None, :] - cents[None], axis=2)
    lab = dist.argmin(1)
    lab[long_] = labels_l
    srt = np.sort(dist, 1)
    conf = np.where(srt.shape[1] > 1, (srt[:, 1] - srt[:, 0]) / (srt[:, 1] + 1e-6), 1.0)
    return lab, conf, best


SYSTEM = re.compile(r"\b(disconnected|update (complete|failed)|server is shutting|shutting down|rolling back|"
                    r"you left the game|rejoin|joining (the|a)\b|equipped|daily reward|you do not own|friend limit|"
                    r"reset character|game pass only|reason,|level up|badge (earned|awarded)|purchase (complete|failed)|"
                    r"you have been|teleporting|loading)\b", re.I)
SAY_VERB = re.compile(r"\b(typed|types|said|says|asked|asks|yelled|yells|screamed|screams|whispered|whispers|"
                      r"announced|announces|shouted|shouts|replied|replies|wrote|writes|goes|type|typing|saying|yelling|"
                      r"screaming|whispering|shouting)\b,?\s+\S", re.I)
NARR_START = re.compile(r"^(what if\b|day \w+|second \w+|rule \w+|everyone who|comment\b|but\b|then\b|so,? (you|he|she|"
                        r"they|the|mom|dad)\b|and (then|when|by|back)\b|now\b|next\b|meanwhile|within|suddenly|by "
                        r"(lunch|midnight|morning|night|day)|this (noob|kid|player)|outside\b|out there|you\b(?! what)|"
                        r"your\b|mom\b(?!\s*[,!.?])|dad\b(?!\s*[,!.?])|he\b|she\b|they\b|it\b|his\b|her\b|a \w+)", re.I)
FIRST = re.compile(r"\b(i|i'm|i'll|i've|i'd|me|my|mine|we|we're|let's|us|our)\b", re.I)
VOCATIVE = re.compile(r"^(sweetie|honey|mom|mommy|mum|dad|daddy|bro|dude|guys|kid|okay|ok|fine|no+|nope|yes|yeah|wait|"
                      r"what|hey|please|can't|won't|don't|stop|give|look|whose|why|seriously|oh|ooh|aw|ah+|ugh|uh|hmm|"
                      r"ha+|wow|help|run|again|easy|buy|hello|hi|thanks|sorry|listen|careful|good luck)\b", re.I)
PARENT = re.compile(r"\b(sweetie|honey|young (man|lady)|kids these days|clean sheets|bedtime|dinner is ready|"
                    r"breakfast is ready|how do you make him)\b", re.I)
TO_PARENT = re.compile(r"^(mom|mommy|mum|dad|daddy)\b[,!.]", re.I)
TO_KID = re.compile(r"\b(kid|sweetie)\b[?!.]?$|^(listen|careful|good luck|then move)", re.I)


def line_kind(s, narr_voice):
    """'narration', 'dialogue' or 'system' (a game / UI voice), with a score for the dialogue guess."""
    t = s["text"].strip().strip('"\u201c\u201d')
    if SYSTEM.search(t) and not FIRST.search(t):
        return "system"
    score = 0
    if s["text"].strip()[:1] in "\"\u201c" or s["text"].strip()[-1:] in "\"\u201d":
        score += 2
    if VOCATIVE.search(t):
        score += 2
    if FIRST.search(t) and not SAY_VERB.search(t):
        score += 2
    if len(t.split()) <= 3 and t[-1:] in "!?":
        score += 1
    if NARR_START.search(t):
        score -= 2
    if SAY_VERB.search(t):                       # the narrator reads a typed / said line inside narration
        score -= 2
    if s["voice"] != narr_voice and s["voice_conf"] >= 0.3:
        score += 3
    return "dialogue" if score >= 2 else "narration"


def protagonist(segs):
    narr = " ".join(s["text"] for s in segs if s["kind"] == "narration")
    you = len(re.findall(r"\b(you|your)\b", narr, re.I))
    third = len(re.findall(r"\b(he|his|him|she|her)\b", narr, re.I))
    if you >= third:
        return "Kid"
    stop = {"Roblox", "Robux", "Day", "Mom", "Dad", "Then", "But", "So", "And", "The", "His", "Her", "He", "She",
            "Now", "Next", "First", "Comment", "Everyone", "What", "This", "That", "One", "When", "It", "A", "In"}
    names = [w for w in re.findall(r"\b[A-Z][a-z]{2,}\b", narr) if w not in stop]
    return max(set(names), key=names.count) if names else "Kid"


def name_speakers(segs, lab):
    """Audio voices (A = the main one) + a speaker for every line: Narrator, the protagonist, Mom, Dad, Game."""
    talk = {c: sum(s["dur"] for s, l in zip(segs, lab) if l == c) for c in set(lab)}
    order = sorted(talk, key=lambda c: -talk[c])
    vname = {c: "voice " + "ABCDEFGH"[i] for i, c in enumerate(order)}
    narr_voice = vname[order[0]]
    for s, l in zip(segs, lab):
        s["voice"] = vname[l]
    for s in segs:
        s["kind"] = line_kind(s, narr_voice)
    hero = protagonist(segs)
    prev = None
    for s in segs:
        t = s["text"].strip().strip('"\u201c\u201d')
        if s["kind"] == "narration":
            s["speaker"], s["why"] = "Narrator", "narration"
        elif s["kind"] == "system":
            s["speaker"], s["why"] = "Game", "game / UI message"
        elif PARENT.search(t):
            s["speaker"], s["why"] = ("Mom" if not re.search(r"\bdad\b", t, re.I) else "Dad"), "parent words"
        elif TO_PARENT.search(t):
            s["speaker"], s["why"] = hero, "talks to Mom / Dad"
        elif TO_KID.search(t):
            s["speaker"], s["why"] = "Mentor", "talks to the kid"
        elif prev and prev["kind"] == "dialogue" and prev["speaker"] in ("Mom", "Dad") and prev["speaker"] != hero:
            s["speaker"], s["why"] = hero, "answers the parent"
        elif prev and prev["kind"] == "dialogue" and s["start"] - prev["end"] < 0.3 and prev["voice"] == s["voice"]:
            s["speaker"], s["why"] = prev["speaker"], "same breath as the line before"
        else:
            s["speaker"], s["why"] = hero, "first-person / reaction line (default: the protagonist)"
        prev = s
    # a separate audio voice keeps one name: the most common text guess among its dialogue lines
    for v in set(s["voice"] for s in segs) - {narr_voice}:
        mine = [s for s in segs if s["voice"] == v and s["voice_conf"] >= 0.3]
        if not mine:
            continue
        hz = np.median([s["hz"] for s in mine if s["hz"]] or [0])
        names = [s["speaker"] for s in mine if s["kind"] != "narration"]
        best = "Game" if hz > 600 else (max(set(names), key=names.count) if names else None)
        for s in mine:
            if (s["hz"] or 0) > 600 and not FIRST.search(s["text"]) and s["kind"] != "narration":
                s["speaker"], s["kind"], s["why"] = "Game", "system", f"very high / robotic line in {v}"
            elif best:
                s["speaker"], s["kind"] = best, ("system" if best == "Game" else "dialogue")
                s["why"] += f"; own voice ({v})"
    return hero


# ---------------------------------------------------------------- tone
def tone(s, base, speaker):
    t = s["text"]
    low = t.lower()
    tags = []
    pz = (np.log2((s["hz"] or base["hz"]) / base["hz"]) * 12) / max(1.5, base["st_sd"]) if base["hz"] else 0.0
    lz = (s["db"] - base["db"]) / max(1.5, base["db_sd"])
    rz = (s["rate"] - base["rate"]) / max(0.4, base["rate_sd"])
    narr = speaker == "Narrator"
    if s["unvoiced"] > 0.6 and lz < -0.6:
        tags.append("whispering")
    if re.search(r"\b(subscrib\w*|comment|like)\b", low):
        tags.append("cheerful")
    if re.search(r"^what if\b", low):
        tags.append("curious")
    if re.search(r"\bplease\b|\bjust (one|five|a few)\b", low):
        tags.append("pleading")
    if re.search(r"\bsweetie\b|\bhoney\b", low) and lz < 0.8:
        tags.append("sweet")
    if re.search(r"\b(ha){2,}\b|\blol\b|\bhehe", low):
        tags.append("laughing")
    shout = lz > 0.9 and pz > 0.7
    if shout:
        if re.search(r"\b(now|stop|off|no|never|get out|give me)\b", low) and not narr:
            tags.append("angry")
        elif re.search(r"\b(no+|my \w+|help|what)\b", low) and not narr:
            tags.append("panicked" if "?" not in t else "shocked")
        else:
            tags.append("excited")
    elif re.search(r"(\?!|!\?)[\"')]*$", t):
        tags.append("shocked")
    elif re.search(r"(\.\.\.|…)[\"')]*$", t) and not tags:
        tags.append("suspense")
    elif "?" in t and not tags:
        tags.append("curious" if narr else ("suspicious" if pz < 0.5 else "confused"))
    if not tags and "!" in t:
        tags.append("excited" if pz > -0.6 else ("angry" if lz > 0.3 else "confident"))
    if not tags:
        if pz > 0.8 or (lz > 0.6 and rz > 0.5):
            tags.append("excited")
        elif lz < -0.9 and pz < -0.4:
            tags.append("sad" if rz < 0 else "soft")
        elif s["range_st"] < 3.0 and pz < 0.2:
            tags.append("deadpan")
        elif rz < -1.0:
            tags.append("soft")
        else:
            tags.append("calm" if narr else "confident")
    if re.search(r"\b[A-Z]{3,}\b", t) and "emphasis" not in tags:
        tags.append("emphasis")
    return tags[:2], dict(pitch_z=round(float(pz), 1), loud_z=round(float(lz), 1), rate_z=round(float(rz), 1))


def baselines(segs, lab):
    out = {}
    for c in set(lab):
        mine = [s for s, l in zip(segs, lab) if l == c]
        hz = np.array([s["hz"] for s in mine if s["hz"]])
        st = 12 * np.log2(hz / 100) if len(hz) else np.array([0.0])
        db = np.array([s["db"] for s in mine])
        rate = np.array([s["rate"] for s in mine])
        out[c] = dict(hz=float(np.median(hz)) if len(hz) else None, st_sd=float(st.std()), db=float(np.median(db)),
                      db_sd=float(db.std()), rate=float(np.median(rate)), rate_sd=float(rate.std()))
    return out


# ---------------------------------------------------------------- report
def structure(segs, total):
    words = sum(s["words"] for s in segs)
    talk = sum(s["dur"] for s in segs)
    chap = [(s["start"], m.group(0)) for s in segs
            for m in [re.search(r"\b(day|second|level|step|rule|part|minute|hour|year|round|stage|chapter)\s+"
                                r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                                r"thirteen|fourteen|fifteen|twenty|thirty|fifty|hundred)\b", s["text"], re.I)] if m]
    cta = [(s["start"], s["text"]) for s in segs if re.search(r"\b(subscrib\w*|comment|like this video|follow)\b",
                                                              s["text"], re.I)]
    return dict(total_s=round(total, 1), words=words, wpm=round(60 * words / max(1, total), 0),
                wps_talking=round(words / max(1, talk), 2), sentences=len(segs),
                questions=sum("?" in s["text"] for s in segs),
                mean_words_per_sentence=round(words / max(1, len(segs)), 1), chapters=chap, ctas=cta)


def pause_tag(gap):
    if gap >= 0.6:
        return " [long pause] "
    if gap >= 0.45:
        return " [pause] "
    if gap >= 0.2:
        return " [break] "
    return " "


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    k = None
    if "--speakers" in sys.argv:
        k = int(sys.argv[sys.argv.index("--speakers") + 1])
        args = [a for a in args if a != str(k)]
    roles = None
    if "--roles" in sys.argv:
        rf = sys.argv[sys.argv.index("--roles") + 1]
        roles = json.load(open(rf))
        args = [a for a in args if a != rf]
    src, srt, out = args[:3]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if "--separate" in sys.argv:
        src = separate(src, out)
    y = load(src)
    fr = frames(y)
    cues = parse_srt(srt)
    segs = [features(s, fr) for s in sentences(cues, fr)]
    lab, conf, sil = cluster(segs, k)
    if not k and sil < 0.3:                      # one voice performs every part (the usual case): one cluster
        lab, conf = np.zeros(len(segs), int), np.ones(len(segs))
    for s, c in zip(segs, conf):
        s["voice_conf"] = round(float(c), 2)
    hero = name_speakers(segs, lab)
    if roles:
        for s in segs:
            mid = (s["start"] + s["end"]) / 2
            hit = next((r for r in roles if r[0] <= mid <= r[1]), None)
            s["speaker"], s["why"] = (hit[2], "hand-checked") if hit else ("Narrator", "hand-checked")
            s["kind"] = "narration" if not hit else ("system" if hit[2] == "Game" else "dialogue")
    names = sorted(set(s["speaker"] for s in segs))
    spk = {n: i for i, n in enumerate(names)}
    base = baselines(segs, [spk[s["speaker"]] for s in segs])
    for s in segs:
        s["tone"], s["z"] = tone(s, base[spk[s["speaker"]]], s["speaker"])
    info = structure(segs, len(y) / SR)
    voices = {}
    for n in names:
        mine = [s for s in segs if s["speaker"] == n]
        hz = [s["hz"] for s in mine if s["hz"]]
        tones = [t for s in mine for t in s["tone"]]
        voices[n] = dict(name=n, lines=len(mine), talk=round(sum(s["dur"] for s in mine), 1),
                         words=sum(s["words"] for s in mine), hz=round(float(np.median(hz)), 0) if hz else None,
                         voices=sorted(set(s["voice"] for s in mine)),
                         tones=", ".join(f"{t} {tones.count(t)}" for t in sorted(set(tones), key=lambda t: -tones.count(t))[:5]),
                         why=mine[0]["why"].split(";")[0])

    # script.txt in the user's format
    blocks, prev_end, cur = [], None, None
    for s in segs:
        gap = 0 if prev_end is None else s["start"] - prev_end
        tagtxt = " ".join(f"[{t}]" for t in s["tone"])
        if cur and cur[0] == s["speaker"]:
            cur[1] += pause_tag(gap) + f"{tagtxt} {s['text']}"
        else:
            if cur:
                blocks.append(cur)
            cur = [s["speaker"], f"{tagtxt} {s['text']}"]
        prev_end = s["end"]
    if cur:
        blocks.append(cur)
    (out / "script.txt").write_text("\n\n".join(f"{n}: {t.strip()}" for n, t in blocks) + "\n", encoding="utf-8")

    # cast.md
    vs = sorted(voices.values(), key=lambda v: -v["talk"])
    L = [f"# Cast sheet: {Path(sys.argv[1]).name}", "",
         f"- Length {info['total_s']} s, {info['words']} words, {info['wpm']:.0f} words/min overall, "
         f"{info['wps_talking']} words/s while talking, {info['sentences']} sentences "
         f"({info['mean_words_per_sentence']} words each), {info['questions']} questions",
         f"- Audio voices: **{len(set(s['voice'] for s in segs))}** (cluster silhouette {sil:.2f}; under 0.30 = one voice "
         f"performs every part, so the speakers below come from the words)",
         f"- Speakers (from words + voice): **{len(vs)}**, protagonist = {hero}; speaker turns: {len(blocks)}", ""]
    if info["chapters"]:
        L.append("- Chapter words: " + " · ".join(f"{t:.1f}s {w}" for t, w in info["chapters"]))
    if info["ctas"]:
        L.append("- Calls to action: " + " · ".join(f"{t:.1f}s \"{w}\"" for t, w in info["ctas"]))
    L += ["", "## Speakers", "", "| Speaker | Lines | Talk | Share | Words | Pitch | Audio voice | Main tones |",
          "|---|---|---|---|---|---|---|---|"]
    talk_all = sum(v["talk"] for v in vs)
    for v in vs:
        L.append(f"| {v['name']} | {v['lines']} | {v['talk']} s | {100 * v['talk'] / max(1, talk_all):.0f}% | {v['words']} | "
                 f"{v['hz'] or '-'} Hz | {', '.join(v['voices'])} | {v['tones']} |")
    L += ["", "## Every line", "",
          "| Time | Speaker (why) | Line | Tone | Hz | dB | w/s | pitch z / loud z / rate z |", "|---|---|---|---|---|---|---|---|"]
    for s in segs:
        L.append(f"| {s['start']:.1f}-{s['end']:.1f} | {s['speaker']} ({s['why']}) | {s['text']} | "
                 f"{', '.join(s['tone'])} | {s['hz'] or '-'} | {s['db']} | {s['rate']} | "
                 f"{s['z']['pitch_z']} / {s['z']['loud_z']} / {s['z']['rate_z']} |")
    (out / "cast.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for s in segs:
        s.pop("_mfcc", None)
    json.dump(dict(info=info, silhouette=round(float(sil), 3), protagonist=hero, speakers=vs, lines=segs),
              open(out / "cast.json", "w"), indent=1, default=float)
    print("\n".join(L[:12]))
    print(f"\nwrote {out}/cast.md, cast.json, script.txt")


if __name__ == "__main__":
    main()
