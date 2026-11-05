# Script guide: titles, scripts, emotions and silent parts (Style B)

This guide was learned from 6 reference videos (~50-56 s each):
- What If Your MOM Started Playing Roblox
- What If MOM Gave You 10 Seconds of Roblox
- What If Your DAD Became the NOOB KING
- What If You Got 1 ROBUX Every Time You Blinked
- What If You HACKED Roblox
- the robux10 voice the user made
- **Set 3 (2026-11-04):** What If You NEVER Stopped Playing Roblox, What If Your BEST FRIEND Quit Roblox (read at 4 fps and every frame at 60 fps; data in `analysis/ref_data/set3_*`)

**How they were analysed:**
- Every video was read at 4 fps (`analysis/frame_log.py`).
- The voice was separated from the music and SFX (`analysis/separate.py`).
- Every silent gap was measured (`analysis/silences.py`).
- The speaker of each line was identified by its pitch and by who is on screen.
- The data is in `analysis/ref_data/set2_*`.

Use this guide for three jobs:
1. **Titles:** when the user asks for titles, give them in this style (section 1).
2. **Scripts:** write a script from a title, with a character and an emotion on every line, in the user's format (sections 2-5).
3. **Videos:** when the user uploads the voice of that script, make the video, handling the silent parts as in section 6.

The style is copied, never the text: do not reuse the reference channel's lines, names or jokes.

---

## 1. Titles

**Formula:** `What If` + **who** + **a power / rule / change** + `Roblox`, with **ONE or two key words in CAPITALS**.

| Pattern | Reference shape | Fresh examples (ours) |
|---|---|---|
| A family member does a gamer thing | What If Your MOM Started Playing Roblox | What If Your GRANDMA Became a Pro Gamer · What If Your DAD Joined Your Obby Team |
| A family member becomes a game role | What If Your DAD Became the NOOB KING | What If Your MOM Became a Roblox ADMIN · What If Your SISTER Became the Final BOSS |
| A strict limit / rule from mom | What If MOM Gave You 10 Seconds of Roblox | What If MOM Banned the JUMP Button · What If MOM Made Roblox Cost 1 CHORE Per Minute |
| You get a strange superpower | What If You HACKED Roblox | What If You Could PAUSE Roblox · What If You Had Infinite ADMIN Commands |
| You earn money for a body action | What If You Got 1 ROBUX Every Time You Blinked | What If You Got 1 ROBUX Every Time You Sneezed · What If Every Step Gave You 100 ROBUX |
| A big number in a short time | 1,000,000 Robux in 10 seconds (robux10) | What If You Had 1 TRILLION Robux for One Day · What If You Got 10 Seconds of ADMIN |

**Rules:**
- **4-9 words**, and always a question ("What if…?").
- It must promise a **clear, visual, absurd idea** that can grow over 5 days.
- The CAPS word is the one that would be the thumbnail text: MOM, DAD, NOOB KING, HACKED, ROBUX, ADMIN, BOSS.
- A **family member** (mom, dad, grandma, sister) or **"you"** is the subject. Mom is the most common antagonist.
- **Spoken, the title is the first line of the script.**
- When asked for titles, give **10**: two per pattern, plus one wild card. Mark the 3 strongest; the most visual and easiest to escalate wins.

---

## 2. Script shape (measured)

| What | Measured in the references | Rule |
|---|---|---|
| Length | 122-143 words, 50-56 s of voice | **120-145 words** (about 50-55 s) |
| Speed | 142-155 words/min overall, 180-190 while talking | Short lines, nothing that needs a slow read |
| Line length | 1-10 words, many 1-3 word fragments ("Tablet. Off. NOW.", "Robux, zero.") | Most lines 3-8 words; a few 1-2 word punches |
| Voice running | 89-93% of the video | Barely any silence (section 6) |
| Speakers | a Narrator plus 1-3 characters; **4-7 character lines** in total | Characters speak the hook reply, the conflict and the ending |
| Chapters | "Day 1 … Day 5" in 4/6 videos, "Second 10 … 5" in 2/6 | Always a counted ladder; the chapter word is a line of its own |
| Call to action | "Everyone who subscribes gets/joins ___" at 26-28 s in every video | Exactly one, right after chapter 4 |
| Ending | "Comment ___ if you ___" around 47-53 s, then a final twist or character line that **loops to the start** | Both, in this order |

### The beat sheet (every reference follows it)

| # | Time | Beat | Who | Emotion | What it does | Reference shapes (paraphrased) |
|---|---|---|---|---|---|---|
| 1 | 0-1.8 s | **Hook**: the title as a question, ≤ 1.8 s, the number/power in it (`lessons.md` 1) | Narrator | curious | States the absurd idea | "What if your dad became the Noob King?" |
| 2 | 1.8-5 s | **Setup**: a quick exchange or a cool line, at most 3 short lines; chapter 1 starts by ~5 s (`lessons.md` 2) | a character (or the narrator) | pleading / smug / confident / whispering | Shows the characters and the conflict | kid begs dad to change his avatar, dad: "Nope."; "Watch this."; "I'm in!" |
| 3 | 7-12 s | **Chapter 1**: the first small, funny result | Narrator + a 1-line character reaction | excited / chuckling | The power works, clumsily | can't even jump; blink → DING, it's real |
| 4 | 12-17 s | **Chapter 2**: a surprising escalation | Narrator | excited / gasping | Bigger and stranger | a golden crown drops; /GIANT |
| 5 | 17-23 s | **Chapter 3**: a huge number | Narrator | excited, emphasis on the number | 1,000,000 / trillion / everything free | "One million noobs join his army" |
| 6 | 23-26 s | **Chapter 4**: it goes public | Narrator | excited | The whole server or class sees it | take over every obby; everyone's staring |
| 7 | 26-29 s | **CTA**: "Everyone who subscribes gets ___" (always tied to the power). **Analytics rule (`lessons.md` 3): one line ≤ 2 s, a curiosity hook right before it ("But on Day 5, something impossible happens…"), the biggest surprise right after** | Narrator | whispering → cheerful | A subscribe button gets pressed on screen | gets ADMIN / joins the noob army / one free blink |
| 8 | 29-35 s | **Chapter 5 = the conflict**: mom or dad steps in | Narrator ("Mom says…") + a character | soft → suspicious / angry | The authority figure arrives | "Tablet. Off. NOW."; "Staring contest, sweetie." |
| 9 | 35-42 s | **Showdown**: the power vs the parent | the characters | pleading / confident / shocked | One clever move each | freeze mom; "Kneel before the King!" |
| 10 | 42-47 s | **Punishment**: everything goes to zero | Narrator | deadpan → sad | The loss, item by item | "Your Robux… Zero."; "Pet, gone."; turns into a noob |
| 11 | 47-49 s | **The parent's sweet ending line** | Mom / Dad | sweet / smug | Irony | "Bedtime, sweetie."; "No more Roblox, sweetie." |
| 12 | 49-52 s | **Twist**: "But then…" one more turn | Narrator | whispering → excited | Opens a new problem | the game updated…; mom forgot one thing… |
| 13 | 47-51 s | **Comment CTA** with ONE keyword, **before** the final punchline, ≤ 1.5 s (`lessons.md` 4) | Narrator | cheerful | "Comment HACK if you'd…" | the keyword is the title's power word |
| 14 | 51-54 s | **Final punchline = loop line**: the last spoken words, leading back into the hook; nothing after it except the REWIND | a character | confused / sneaky | Ends mid-action, so the video restarts | "Slash… REWIND!"; "Wait, which button goes back?" |

### How the two set-3 scripts fit the beat sheet
| Beat | Never stopped | Best friend quit |
|---|---|---|
| 1 Hook (0-2.3 s) | "What if you never stopped playing Roblox?" | "What if your best friend didn't want to play Roblox anymore?" |
| 2 Setup (2.6-9 s) | a **3-step list** "Not for dinner, not for bed, never." → Mom: "Sweetie, time to stop playing." → Kid: "Can't. I'm on a win streak." | Friend: "Roblox is for babies. I quit." → Kid: "You what?" |
| 3-6 Day 1-4 (9-24 s) | dinner (spaghetti + tablet) → mom hides the tablet → microwave → shower in a plastic bag → playing asleep | game invite → DECLINED → legendary dragon gift → RETURN TO SENDER → a giant sign → the whole server spams COME BACK |
| Each Day | **action → the parent/friend's counter → the kid's absurd workaround** in two lines | **the kid's attempt → the friend's one-word rejection** ("Declined.", "Return to sender.") |
| Big number | "96 hours straight. New world record." | "A thousand players spamming come back." |
| 7 CTA (24.9-31.6 s) | "Everyone who subscribes gets unlimited screen time." | "Everyone who subscribes gets a best friend who never quits." |
| 8 Day 5 = conflict (32-38 s) | mom shuts off the power for the whole house | you peek through their window |
| 9-10 Showdown / loss | phone at 1 % battery; the game begs; the servers are tired | the secret account "Totally not me 1, 2, 3" → the confession |
| 11 Turn | Kid: "Fine, I'll stop." | Narrator: "It's the first jump. The tutorial one." |
| 13 Comment CTA (47-52 s) | "Comment one more if you'd never stop either." | "Comment carry if you'd help your friend too." |
| 14 Loop line | Kid: "Okay, one more game." | Friend: "I fell again." |

**What set 3 teaches for new scripts:**
- **Day lines are two-beat jokes**: an action, then the counter-move ("Day two, mom hides the tablet. So you play on the microwave."). The second half starts with "So, you…" or is a single result word ("Declined.").
- **The antagonist can be anyone close** (mom, a best friend, the game itself). A friend who "quits" is a secret fan: the twist reveals the real reason (stuck on the easiest jump).
- **Absurd places beat bigger numbers**: microwave, shower in a plastic bag, asleep. Each is one literal picture.
- **The comment keyword is the story's verb** ("one more", "carry"), not only the title word.
- **The last line undoes the ending** ("Okay, one more game.", "I fell again.") and loops into the hook.
- Length: 126 and 135 words in 53-55 s (set 1-2: 122-143).

### Escalation rules
- **Numbers climb by orders of magnitude**: 1 → 100 → 1,000,000 → 900 trillion, then crash to **zero**.
- **Every chapter is something the camera can show literally**: an object, a UI panel, a crowd, a counter. No abstract lines.
- **A running gag** comes back 2-3 times: DING!, "sweetie", the slipper, the noob, the button.
- **The parent's last word is "sweetie"** (warm words, cold meaning). It appears in 4 of 6 videos.

---

## 3. Script format (the user's format, for the voice tool)

```
Narrator: [curious] What if ... ? [break] [whispering] Watch this. [break] [excited] Day 1, ...

Mom: [suspicious] ...?

Kid: [confident] [chuckling] ...

Narrator: [soft] ... [break] [deadpan] ... [long pause] [whispering] But ... [break] [cheerful] Comment "WORD" if ...
```

**Format rules:**
- **One block per speaker turn**: `Speaker: [emotion] text`, with a blank line between blocks. Narrator blocks can be long; character blocks are 1-2 short lines.
- **1-2 emotion tags** right before each sentence or fragment. Change the tag whenever the feeling changes, even inside a block.
- **Pause tags** decide the silence (section 6), so use them carefully:
  - `[break]` between beats or chapters: ≈0.2-0.4 s, the reference norm.
  - `[pause]` once or twice, right before a big reveal number: ≈0.5 s.
  - `[long pause]` **at most once**, before the final twist: ≈0.6-0.7 s, never more.
- **Emphasis**: `[emphasis]` plus CAPS on the single key word or phrase ("[emphasis] ONE MILLION ROBUX!"). That word becomes a coloured caption and the visual's punch.
- **Write numbers as words** where the voice should say them ("a hundred thousand"), and CAPITALISE shouted words.
- **Stage directions are never written**: only spoken text and tags. The visuals come from the words.

---

## 4. Emotions (what each tag is used for)

| Speaker | Tag | Use it on | Example shape |
|---|---|---|---|
| Narrator | [curious] | The hook question | "What if you … ?" |
| Narrator | [whispering] | Secrets, "watch this", "mom walks in", "but then…" | low and sneaky, right before a turn |
| Narrator | [excited] | Every win and chapter result | "Day 3. A MILLION…" |
| Narrator | [gasping] / [shocked] | A surprise drop / a glitch | "a golden ticket falls out!" |
| Narrator | [suspense] | A counter spinning, a countdown | "the counter starts spinning…" |
| Narrator | [chuckling] / [laughing] | An ironic detail | "…while folding laundry." |
| Narrator | [cheerful] | Both calls to action | "Everyone who subscribes…", "Comment…" |
| Narrator | [soft] | The calm before the parent arrives | "Day 5…" |
| Narrator | [deadpan] | The punishment list | "Refund complete. Robux, zero." |
| Narrator | [sad] | The loss | "Pet, gone." |
| Mom | [suspicious] → [angry] → [sweet] | Questioning, the order, the ironic sign-off | "Whose card…?", "Tablet. Off. NOW.", "…sweetie." |
| Dad | [proud] / [deadpan] / [confused] | Silly pride, a flat "Nope.", the loop question | "Nope.", "Wait, which button…?" |
| Kid ("you") | [pleading] / [confident] / [panicked] / [crying] | Begging, smug wins, the loss | "Just five more minutes!", "Mine, obviously.", "My Robux!" |
| Grandma / sibling / noob / crowd | [excited] / [mocking] | One-line cameos | "Come on…!", "LOL noob" |

Measured voices: the kid's lines sit high (320-520 Hz), dad's low (~100 Hz), mom in the middle (~200-240 Hz), and the narrator calm and low on facts (100-140 Hz) but rising on wins (220-330 Hz). Pick voices with that contrast.

### Who speaks when (speaker maps measured with pitch + the face on screen)
| Video | Narrator | Character lines (in order) |
|---|---|---|
| Dad Noob King | hook, Day 1-5, CTA, "One bonk…", "Comment…" | Kid: "Dad, you have to change your avatar!" · Dad: "Nope." · Dad: "Classic." · Dad: "Kneel before…!" · Kid: "Dad, no! I spent all my Robux…" · Kid: "My Robux!" · Dad: "Now, who knows how to jump?" · Dad: "Wait, which button goes back?" |
| Blink Robux | hook, Day lines, "Mom thinks…", "Mom has never lost…", "Then mom blows…", twist, CTA | Kid: "It's real!" · Kid: "100 Robux!" · Mom: "Why do you keep winking at me?" · Mom: "Staring contest, sweetie. If you blink, no more Robux." · Kid: "Must. Not. Blink." · Kid: "No!" · Mom: "No more Robux, sweetie!" |
| Mom plays | hook, Day lines, CTA | Mom: "What's so special about this blocky game? Give me that." · Mom: "Which button is jump?" · Kid: "It's 3 a.m. Mom." · Mom: "Just one more round." · Kid: "Did you spend my Robux?" · Mom: "It was for a pet. For you, sweetie." |
| Hacked (SRT + pitch) | hook, "Just one line of code.", Day lines, CTA, "Mom froze, mid-sentence.", "Then the screen turned red.", "Your avatar turns into a noob. Your Robux, zero.", "Comment…" | Kid: "I'm in!" (429 Hz) · Mom: "Tablet. Off. NOW." (~207 Hz) · Kid: "Slash… freeze… Mom." (376 Hz) · Kid: "Hacker detected!" (408 Hz, shocked close-up) · Mom: "Unfrozen!" (437 Hz shout; the SRT misheard it as "I'm frozen") · Mom: "Bedtime, sweetie." (302 Hz) · Kid: "Slash, rewind!" (432 Hz, the loop line) |

| Never stopped (set 3) | hook, "Not for dinner, not for bed, never.", Day 1-5 lines, "96 hours straight. New world record.", CTA, "So you switch to your phone. 1 % battery.", "Even the servers are tired.", "Comment one more…" | Mom: "Sweetie, time to stop playing." (254 Hz, sweet → firm) · Kid: "Can't. I'm on a win streak." (293 Hz, cocky) · **the game itself**: "Please, take a break." (578 Hz, a robotic/pleading voice in a SYSTEM MESSAGE) · Kid: "Fine, I'll stop." (160 Hz, exhausted, slow 1.6 w/s) · Kid: "Okay, one more game." (363 Hz, sneaky grin; the loop line) |
| Best friend quit (set 3) | hook, Day 1-5 lines, "Declined.", "Return to sender.", CTA, "You peek through their window. They're playing Roblox on a secret account.", "It's the first jump. The tutorial one.", "Comment carry…" | Friend: "Roblox is for babies. I quit." (192 Hz, cool, dismissive) · Kid: "You what?" (274 Hz, shocked) · Kid (sign): "Please come back." (321 Hz, pleading) · Kid: "Totally not me 1, 2, 3." (355 Hz, reading the fake name in disbelief) · Friend: "Okay, okay. I didn't quit. I've been stuck on the same obby jump for a whole month." (376-517 Hz, caught → confessing fast) · Kid: "Bro, I'll carry you." (238 Hz, warm, slow 1.7 w/s) · Friend: "I fell again." (339 Hz, deadpan; the loop line) |

**The pattern:**
- **The kid reacts in the first person** to his own wins ("It's real!", "100 Robux!").
- **Set 3 adds two speaker kinds:** **the game / a device talks** (a SYSTEM MESSAGE begging "Please, take a break", servers that are "tired"), and **the antagonist is a friend**, not a parent: the friend's cool quit line, then a caught confession.
- **Set 3 ends on the antagonist's or kid's 3-5 word confession / relapse**: "Okay, one more game.", "I fell again." It undoes the whole story in one line, so the loop back to the hook feels earned.
- **The parent gets the orders and the "sweetie" lines.**
- **The narrator owns** the hook, the chapter words, the facts, both calls to action and the punishment list.
- **Two speakers can share one breath**: "Tablet, off, now, slash, freeze, mom" is mom's order cut off by the kid's command, with a 0.2 s gap. Write it as two blocks; the video cuts between their close-ups in that gap.
- **SFX words are not spoken.** "Blink… DING!", "BONK!", "POOF!", "SLAM!" are on-screen text over an SFX, filling a 0.5-1.5 s visual beat while the voice pauses or keeps going. Write them in the script only as a `[break]`; the video adds them.

---

## 5. Bending any topic or script into this style

When the user gives another topic, or a script from another niche, keep its **core idea** and rebuild it on the beat sheet:

1. **Find the power or rule.** What changes? (a superpower, a limit, a role, money per action)
2. **Move it into Roblox**: obby, server, avatar, Robux, admin commands, pets, the noob, the shop, the leaderboard.
3. **Add the family antagonist**: mom (default), dad, grandma or a sibling. The parent wins at the end, with a "sweetie" line.
4. **Ladder it over Day 1-5** (or Second 10-1 when the topic is about time), with numbers climbing by ×100.
5. **Make every line visual**: replace explanations with a thing that happens on screen.
6. **Add the two calls to action, the zero-crash, the "But then…" twist and a loop line** that leads back into the hook.
7. **Title**: put it in a section 1 pattern.

**Example of bending.** Topic given: "a kid who never does homework".
- Title: *What If HOMEWORK Gave You Robux?*
- Day 1: one page = 1 Robux. Day 2: you finish the whole book. Day 3: you do your class's homework, a million Robux. Day 4: the teacher gives you an A+++ trophy.
- CTA: "Everyone who subscribes gets a free homework pass."
- Day 5: mom: "If you're so smart… do the dishes, sweetie."
- Twist: the game updates; now Robux cost homework. Comment "HOMEWORK…".
- Loop: "Wait… is this on the test?"

---

## 6. Silent parts: how long they are, and what is on screen

### Measured (`analysis/silences.py` on the voice stem)

| Video | Voice running | Gaps per 10 s (≥0.25 s) | Gap median | Longest gap | Gaps with an SFX hit | Silence after the last word |
|---|---|---|---|---|---|---|
| Dad Noob King | 93% | 0.4 | 0.28 s | 0.29 s | 2/2 | 1.03 s |
| Mom plays | 92% | 1.0 | 0.29 s | 0.53 s | 3/5 | 0.36 s |
| Blink Robux (SRT given) | 91% | 1.6 (gaps ≥0.2 s) | 0.24 s | 0.33 s | 0/9 | 0.53 s |
| 10 Seconds (SRT given) | 89% | 1.6 | 0.29 s | 0.54 s | 4/8 | 0.54 s |
| Hacked (SRT given) | 89% | 1.5 (gaps ≥0.2 s) | 0.28 s | 0.71 s (the gap before "Day three", filled by the DAY card + SFX) | 3/8 | 0.70 s |
| robux10 (user's voice) | 91% | 0.2 | 0.55 s | 0.55 s | (no SFX in a voice file) | 0 s |
| Never stopped (set 3) | 86% | 1.7 | 0.30 s | 0.52 s | 6/9 | 1.34 s (rewind) |
| Best friend quit (set 3) | 90% | 0.4 | 0.33 s | 0.40 s | 1/2 | 0.99 s (rewind) |

**The rules that follow:**
- **There is almost no silence.** The voice starts on the first frame (0-0.4 s) and runs 89-93% of the time.
- Gaps between lines are **0.2-0.4 s**; the longest anywhere is **0.71 s**.
- **Nothing is ever still in a gap.** The picture keeps moving: idle bounce, a cut, a pop. Half or more of the gaps carry an SFX.
- The caption of the last words **stays on screen through the gap**.

### What happens on screen in each kind of gap (read frame by frame)

| Where the gap is | Length | What the picture does | Sound |
|---|---|---|---|
| Before a chapter word ("Day 3.", "Second 7") | 0.2-0.4 s | **Cut to the new place; the painted DAY card starts drawing inside the gap**, so it is fully in when the word is said | Swoosh/pop on the card, then a hit on the word |
| After a punchline / result | 0.25-0.5 s | **Reaction hold**: the face snaps to a new expression (tears, sweat, star eyes), a crowd reacts, a counter finishes rolling | Hit, ding or pop |
| Between two speakers | 0.2-0.3 s | **Cut to the next speaker's close-up already in the gap** (reaction shot) | Usually none, or a small pop |
| Before the big reveal (`[pause]`) | 0.4-0.6 s | **Push-in / suspense**: the camera creeps toward the object, shake lines, light builds; the reveal pops on the word | Riser or tick, then a boom |
| Before the twist (`[long pause]`) | 0.6-0.7 s | **The scene darkens or freezes** (a pause icon, a red screen, a spotlight); slow push on a face | Music dips; one low hit |
| After the last word | 0.4-1.0 s | **REWIND montage**: "◀◀ REWIND" label and scanlines, the previous shots flash **backwards** (~0.15-0.25 s each), landing exactly on the first frame | Whoosh / rewind sweep |

### Every silent part in all 5 references (41 gaps ≥ 0.2 s, read frame by frame)
Each gap was looked at in 3 frames (start, middle, end); the SFX column comes from the music+SFX stem. The per-gap frames are made by `analysis/silences.py` (data in `analysis/ref_data/*_silences.json`).

| Video | Time | Length | Line before → line after | What the picture does in the gap | SFX |
|---|---|---|---|---|---|
| 10 Seconds | 6.03 | 0.21 | "…go to bed." → "10 seconds?" | Mom's "BED." caption holds, then a **hard cut to the kid's shocked close-up** before he speaks | – |
| 10 Seconds | 13.69 | 0.37 | "…in one jump." → "Second 9…" | **Celebration hold**: the kid at STAGE 100 with confetti; the "JUMP." caption stays | – |
| 10 Seconds | 17.28 | 0.22 | "One punch, KO!" → "Second 8…" | **K.O. sticker holds**, the boss flies off-screen, POW fades | – |
| 10 Seconds | 24.46 | 0.30 | "…into a toaster." → "Second 6…" | Toaster gag holds with "DING!", then a **cut to the crowd** for the next line | – |
| 10 Seconds | 30.99 | 0.28 | "…whole game." → "4…" | LEGENDARY pet holds, then a **cut to mom's red-lit face with "FOUR…"** already on screen | hit |
| 10 Seconds | 32.29 | 0.28 | "4…" → "3…" | Countdown: **cut to the kid scared, the timer pill turns red "0:03"**, shake lines | hit |
| 10 Seconds | 43.49 | 0.41 | "…speedrunner." → "Plus 10 seconds." | The **+10 SECONDS shop card slides in, a finger taps BUY**, "KA-CHING!" | ka-ching |
| 10 Seconds | 49.41 | 0.54 | last word → end | **◀◀ REWIND**: shots flash backwards and land on the first frame | rewind |
| Mom plays | 2.57 | 0.21 | hook → "What's so special…" | Mom's crazy close-up holds, then a **cut to mom grabbing the tablet** | – |
| Mom plays | 6.86 | 0.26 | "Give me that." → "Day 1." | The tablet close-up **zooms into the screen**, landing in the game world | – |
| Mom plays | 12.63 | 0.53 | "…for 10 minutes." → "Which button is jump?" | The noob **bonks into the wall again** (impact star, dizzy stars), then a cut to mom's angry face | thud |
| Mom plays | 24.97 | 0.24 | "Day 4." → "She's number one…" | The K.O. card holds, then a **cut to the leaderboard** | – |
| Mom plays | 32.25 | 0.21 | "It's 3 a.m. Mom." → "10 seconds." | Mom gaming at night: **shake lines and sweat**, the "3 A.M." caption holds | pop |
| Mom plays | 35.70 | 0.29 | "Then you go to bed." → "Just one more round." | The kid walks into frame with the clock: a **two-shot reaction** | – |
| Mom plays | 38.00 | 0.25 | "Just one more round." → "Did you spend my Robux?" | **The Robux counter drops 3,807 → −12,500 → 0** | tick/hit |
| Mom plays | 44.50 | 0.34 | "…grandma logged in." → "Come on, Gigi." | BONK on the kid, "sweetie!", then a **cut to a dark silhouette** (grandma reveal) | bonk |
| Mom plays | 50.38 | 0.36 | last word → end | **REWIND** blur back to the first frame | whoosh |
| Dad Noob King | 29.66 | 0.29 | "…joins the noob army." → "Day 5." | The NOOB ARMY card holds, then a **cut to the throne room**, where the DAY card starts drawing | swoosh |
| Dad Noob King | 40.64 | 0.20 | "…on this skin!" → "One bonk…" | **Cut to the wide shot**: the king raises his scepter over the kid | – |
| Dad Noob King | 45.43 | 0.20 | "…a noob now." → "My Robux!" | **Cut to the kid at home, shocked**, sweat appearing | – |
| Dad Noob King | 49.97 | 0.26 | "…how to jump?" → "Comment noob…" | "*CRICKET NOISES*" banner and a sweat drop on dad's face (**an awkward-silence gag**), then a cut to the comments | crickets |
| Dad Noob King | 54.94 | 1.03 | last word → end | **REWIND montage** of 3-4 earlier shots, ending on the first frame | rewind |
| Blink | 10.10 | 0.22 | "100 Robux!" → "Day 2." | The coin pile holds, then a **cut to the kitchen** (DAY card next) | – |
| Blink | 22.14 | 0.21 | "…in the game!" → "Day 4." | **Cut to the classroom** | – |
| Blink | 28.95 | 0.24 | "…one free blink." → "Day 5." | Cut to mom and kid at the table with **mom's angry crossed arms** | – |
| Blink | 37.00 | 0.33 | "…no more Robux." → "Mom has never lost…" | ROBLOX vs face split, then a **whip-pan to the trophy shelf** | – |
| Blink | 39.53 | 0.27 | "…staring contest." → "One hour…" | The staring two-shot holds (eyes sparkling), then a **blur transition to the clock** | – |
| Blink | 40.77 | 0.24 | "One hour…" → "three hours" | **Time-lapse**: the clock hand spins, blurred | – |
| Blink | 41.96 | 0.21 | "THREE hours…" → "Must." | The two-shot at night: **lighting changed to dark blue** (time passed) | – |
| Blink | 50.20 | 0.33 | "…sweetie!" → "But then the game updated." | The tablet put away ("sweetie."), then a **cut to the kid's sad face** | – |
| Blink | 54.17 | 0.24 | "…costs one Robux." → "Comment blink…" | The kid rubs his red eyes; **the counter keeps ticking down** | tick |
| Blink | 56.15 | 0.53 | last word → end | **REWIND** blur back to the first frame | rewind |
| Hacked | 5.43 | 0.20 | "I'm in!" → "Day one…" | **Cut to the game spawn pad** with the avatar | – |
| Hacked | 14.08 | 0.71 | "…bigger than the map." → "Day three…" | The giant's "HEHE!" **laughing close-up**, then a cut to the spawn where the DAY 3 card draws | laugh pop |
| Hacked | 26.40 | 0.42 | "…gets admin." → "Day five…" | The ADMIN wink holds, then a **cut to the night bedroom**, the DAY 5 card drawing | swoosh |
| Hacked | 32.01 | 0.23 | mom "…NOW." → kid "Slash…" | **Cut from mom's close-up to the kid's smug close-up** (the turn change) | pop |
| Hacked | 35.12 | 0.32 | "…freeze, mom." → "Mom froze…" | The kid's grin, then a **cut to mom in an ice block** | ice crack |
| Hacked | 37.57 | 0.32 | "Mid-sentence." → "Then the screen turned red." | **Frozen frame with a ⏸ pause icon** on mom's face, then back to the room | – |
| Hacked | 41.26 | 0.20 | "…into a noob." → "Your Robux…" | "DETECTED?!" close-up, then a **cut to the avatar at spawn** | – |
| Hacked | 49.04 | 0.23 | "Bedtime, sweetie." → "Comment hack…" | Mom leaves with hearts; the **kid peeks from under the blanket** | – |
| Hacked | 54.31 | 0.70 | last word → end | **◀◀ REWIND** ("Roblox?" hook shot flashes), landing on the first frame | rewind |

### Set 3 gaps (read frame by frame at 60 fps)
| Video | Gap at | Length | Between | What is on screen | SFX |
|---|---|---|---|---|---|
| Never stopped | 17.25 | 0.28 | "…microwave." → "Day three…" | **Cut to the pink shower curtain** before the DAY 3 card writes on | swish |
| Never stopped | 32.05 | 0.45 | "…screen time." → "Day five…" | **Cut to the empty hallway with the MAIN POWER panel**; the DAY 5 card writes on as mom walks in | pop |
| Never stopped | 37.06 | 0.52 | "…whole house." → "So you switch…" | The house's **lit windows go dark one by one** (a reaction hold), then a cut to the kid's face lit by the phone | clunk |
| Never stopped | 40.26 | 0.40 | "1 % battery." → "Please, take a break." | The kid's panicked face with sweat, then **the SYSTEM MESSAGE pops** on the phone | ding |
| Never stopped | 44.3-45.1 | ~0.7 (music) | "…are tired." → "Fine, I'll stop." | Back in the bedroom: the kid yawns, **steam puffs from his ears**; a slow beat before the tired line | – |
| Best friend | 28.52 | 0.25 | "…never quits." → "Day 5." | **Cut to the house at night** before the DAY 5 card | – |
| Best friend | 46.92 | 0.40 | "…tutorial one." → "Bro, I'll carry you." | The friend falls off the tutorial jump into the water (**splash**), then the kid **joins the game** (toast at the top) | splash |
| both | end | 1.0-1.3 | last line → loop | **◀◀ REWIND**: 4-5 earlier shots backwards (~0.25 s each) to the first frame | rewind |

Set 3 confirms the rules below: no gap over 0.52 s in the middle, a cut or a pop inside every gap, and a reaction hold (lights going out, a yawn) is the only "still" moment.

### What the 41 gaps show (patterns)
1. **The voice never really stops.** 39 of 41 gaps are 0.20-0.54 s. Only two run longer: Hacked "Day three" (0.71 s) and the Dad ending (1.03 s). There is no gap before the first word (voice from 0.35-0.4 s) and no music-only intro.
2. **Where the gaps fall:**

   | Position | Gaps | Share |
   |---|---|---|
   | Before a chapter word ("Day N" / "Second N") | 11 | 27% |
   | Between two speakers | 9 | 22% |
   | After a punchline or result | 9 | 22% |
   | Countdown / time-lapse steps | 5 | 12% |
   | The ending | 5 | 12% |
   | A turn ("But then…") | 2 | 5% |
3. **Something always changes in the gap.**
   - In 30 of 36 middle gaps there is a **hard cut inside the gap**: the next shot appears before its words.
   - The other 6 are **reaction holds**: an expression snap, the counter rolling, the "*CRICKET NOISES*" gag.
4. **The caption of the last words stays on screen** through the gap. It is never empty.
5. **SFX:** about 40% of the gaps carry one (a hit on the countdown, ka-ching, bonk, crickets, rewind). The rest are covered by the music. There is no total silence anywhere.
6. **The ending is always a REWIND**, 0.36-1.03 s after the last word: 3-5 earlier shots flash backwards, with "◀◀ REWIND" and scanlines, landing on the first frame.
7. **Time passing** (one hour → three hours, 3 a.m.) uses the gaps for a **clock time-lapse plus a lighting change** (day → night blue).
8. **An intentional awkward silence** is shown as a gag: the "*CRICKET NOISES*" banner, a sweat drop and a cricket SFX. Use it after a character's dumb question.

### Rules for our videos (when the user uploads a voice)

1. **Measure the voice first:** `python3 analysis/silences.py - <voice> - <subs.srt> output/<story>/silences`. It lists every gap with the line before and after.
2. **If any gap is over 0.8 s**, or the voice runs below ~88% of the time, tighten the voice before planning:
   `python3 assembler/tighten_voice.py <voice> <subs.srt> output/<story>/voice.wav output/<story>/subs.srt --max 0.6`.
   This trims each long pause to 0.6 s and shifts the SRT to match. Then align the words on the tightened voice.
3. **Plan a visual for every gap**, using the table above:
   - Start the next shot in the gap (the cut lands 0.1-0.25 s before the next line's first word).
   - Put a reaction or expression snap on the previous shot's last 0.2 s.
   - Place one SFX in the gap (pop, hit or ding), except between two speakers.
4. **A `[pause]` reveal** gets a short creeping push (key 0.4-0.6 s) that lands on the reveal word.
5. **A `[long pause]` twist** gets `MUSIC dips=[(t0, t1)]`, a darker tint or a spotlight, and a slow push on the face.
6. **The ending:** the last 0.5-1.0 s after the final word is a `sets.rewind_shot` montage of 4-6 earlier shots played backwards, ending on the first frame. This replaces the plain `s_end` freeze.
7. **The captions** (when asked for) stay on the last words through a gap; `assembler/captions.py` already holds each caption until the next unless the pause is longer than 0.6 s.

---

## 7. Long videos (~8 min): learned from 2 references (2026-11-05)

The user sent the audio + SRT of two long videos in this same visual style:
- **What If the WHOLE WORLD Became Roblox?** (8:08, 7 days)
- **What If You Got Sucked INTO Roblox?** (8:26, 5 days)

**Data** (in `analysis/ref_data/`):
- `long_*_script.txt`: the full scripts in the user's format, every sentence with its speaker and emotion. Study them, never reuse the lines.
- `long_*_cast.md`: every line with its pitch, loudness and speed.
- `long_*_roles.json`: the hand-checked speaker times.
- `long_*.srt`.

**How they were analysed:**
- The voice was separated from the music (`separate.py`).
- `analysis/voice_cast.py` measured every sentence (see section 8).
- The speakers were hand-checked from the story; the character emotions were hand-corrected.

Everything in sections 1-6 is for ~55 s Shorts. Use this section when the user asks for a **long video** title, script or analysis.

### 7.1 Long titles
**Formula:** `What If` + **you / the WHOLE WORLD / your family / your school** + **a crossover verb** + `Roblox?`
- Real life and Roblox **merge**: the world becomes Roblox, or you go into it.
- CAPS go on the **scope** word (WHOLE WORLD) or the **direction** word (INTO).
- 6-8 words, always a question that ends in "Roblox?".

| Pattern | Reference | Fresh examples (ours) |
|---|---|---|
| The real world turns into Roblox | What If the WHOLE WORLD Became Roblox? | What If Your SCHOOL Became Roblox? · What If Your HOUSE Turned Into an OBBY? · What If Real Life Had LAG? |
| You go into Roblox | What If You Got Sucked INTO Roblox? | What If You Got TRAPPED in a Roblox Obby? · What If You Woke Up INSIDE Your Roblox Avatar? |
| Roblox comes out | – | What If Roblox Came INTO the Real World? · What If Your Roblox Avatar Came to LIFE? |
| One game rule hits real life | (Rule one … Rule four in WHOLE WORLD) | What If Real Life Had a RESET Button? · What If Real Life Had ADMIN Commands? · What If Real Life Had a CHAT FILTER? |
| A family member goes in | (Mom / Dad holding the tablet in SUCKED) | What If DAD Got Sucked Into Roblox? · What If Your Whole FAMILY Lived in Roblox? |

**The test for a long title:** it must give **5-7 different days**: home, school, money, parents playing, the game's owner or admins, a scary game, a shutdown. One gag is enough for a Short; a long title needs a whole world.

**When asked for long titles:** give 10, two per pattern, and mark the 3 strongest. Our own ideas only.

### 7.2 Measured shape
| What | WHOLE WORLD | SUCKED INTO | Rule for our long scripts |
|---|---|---|---|
| Length | 488 s | 506 s | **8-8.5 min** |
| Words | 1,078 (132/min) | 1,073 (127/min) | **1,000-1,150 words** |
| Speed while talking | 2.9 words/s | 2.9 words/s | same as Shorts |
| Sentences | 180, median 5 words; 31 % ≤ 3 words | 253, median 4 words; 48 % ≤ 3 words | short sentences, many 1-3 word fragments |
| Character lines | 59 of 180 sentences (25 % of words) | 105 of 253 (34 % of words) | **30-35 % of sentences are character lines** |
| Days | 7 (Day 1-4 51-61 s, Day 5-6 45-50 s, **Day 7 = 107 s climax**) | 5 (Day 1 105 s, Day 2 88 s, Day 3 68 s, Day 4 61 s, **Day 5 = 102 s climax**) | 5 or 7 days, 45-105 s each; **the last day is the longest** |
| Intro before Day 1 | 36.5 s | 51.8 s | **35-52 s** |
| Subscribe CTA | 4:18 (53 %), 12 s | 5:13 (62 %), 13 s | **at 53-62 %, between two days, 10-13 s** |
| Comment CTA | 7:52 (97 %) | 8:09 (97 %) | **≈ 97 %, then the loop line** |
| Pauses between sentences | median 0.52 s, 36 over 0.8 s | median 0.48 s, 28 over 0.8 s | longer breaths than Shorts |
| Long pauses (1.2-2.2 s) | before every Day, both CTAs and the resolution | the same | **1.3-2 s before each "Day N" and each CTA** |
| Dramatic silence | – | **3.5 s** after "closer and closer and…" (the moment you are pulled in) | at most one, at the transformation |
| Voice running | 83 % | 85 % | – |
| Music + SFX under the voice | −17 dB, rising to −11 dB in the gaps | −16.5 / −11 dB | **music ≈ 16-17 dB under the voice**, louder in gaps |
| Music | ~125 bpm, centred on G | ~117 bpm, centred on D | `music_game` (G, 128 bpm) is close |

### 7.3 The long beat sheet (both references follow it)
| # | Time | Beat | WHOLE WORLD | SUCKED INTO |
|---|---|---|---|---|
| 1 | 0-4 s | **Hook**: the title as a question | Narrator: "What if you woke up and the whole world became Roblox?" | "What if you got sucked into Roblox?" |
| 2 | 4-11 s | **Stakes flash-forward**: the number of days + how bad the last day gets | "Seven days, one game, and by day seven, the world had 60 seconds left." | "…trapped inside the game for five whole days. And by day five, you were running for your life!" |
| 3 | 12-18 s | *(optional)* **Cold open**: the climax scene played early, with dialogue + a deadpan narrator tag; repeated word for word at the real climax | – | Kid: "Mom! Mom! Press leave! Please, press leave!" · Narrator: "Mom couldn't hear you. Mom was eating chips." (again at 7:01) |
| 4 | 11-25 s | **"I can explain"**: the Kid rewinds the story, the Narrator starts it | Kid: "Okay, okay, I can explain." · "It all started with a pop-up." | Kid: "Okay, I can explain." · "It all started with one jump." |
| 5 | 20-50 s | **The trigger**: a time stamp → the cause → the Kid's careless line → an ominous one-liner → a silent beat | "Last night, 2 a.m." → pop-up "Turn the world into Roblox? Yes or yes." → Kid: "Sure, whatever." → "You pressed yes." | "Friday night." → stuck on a jump for 3 h → Kid: "If I was in there, I'd make that jump easy." → "Careful what you wish for." → 3.5 s silence |
| 6 | Day 1 (~1-1.7 min) | **Discovery**: body and home turn into Roblox, as a quick question-answer list; the Kid reacts to his own body; every running gag gets its first stage | hands = blocks, bed? plastic, floor? studs, name tag, toothbrush in the hotbar "Equipped.", stairs take half your health, Mom's words in a chat bubble, Dad walking into a wall | landing on a spawn point, face is a sticker, the emote menu (Happy. Sad. Angry. Super happy.), everyone jumping, XXProGamerXX dancing |
| 7 | Day 1-2 | **The rules**: numbered, each one with its gag at once; every rule pays off later | Day 2: "Rule one … Rule four" (jump ×5 → obby; red = lava; respawn on clean sheets; idle → disconnected) | the **mentor** (an old noob, here since 2006) gives "only two rules" + a time rule (1 day = 10 minutes out there) |
| 8 | Days 2-4 (45-90 s each) | **One new domain a day**, 4-8 gags each: narrator setup → a character punch line or a deadpan narrator tag | neighbourhood obby → school (NPC teacher, math obby, badge) → money becomes Robux (ice cream game passes, Dad a free player, Mom's 40 hats) | Mom holds the tablet (walks you into walls, spins the camera, avatar shop tutu) → Dad's pizza tycoon → you are free and build LEAVE |
| 9 | 53-62 % | **Subscribe CTA, as a joke with a reward AND a punishment**; it comes right after a cliff-hanger and right before the next day's turn (`lessons.md` rule 3) | "Oh, and everyone who subscribes gets a golden name tag in the new world. … Everyone who doesn't? Default noob avatar forever." → "Day five, something is wrong." | "…gets a VIP pass for when you get sucked in! Your own server! No chat filter! Don't subscribe? Dad gets your tablet! Enjoy the pizza!" → "Day four. Dad is snoring. Nobody is holding the tablet." |
| 10 | 2nd-last day | **"Something is wrong"**: the threat appears, the tone drops to whispering / suspense | lag (ping 9,000, delayed "Ow."), then the **owner's mouse cursor** editing the world | the dog's paw joins "the scariest game on Roblox" |
| 11 | last day (100-110 s) | **Climax**: a countdown (60 → 30 → 10 s) or a chase. The Kid's plan uses earlier setups, and **every earlier character returns** | server shutdown; the whole town stacks into a tower (Mom in 40 hats, the lemonade kid, the bully, Dad's T-pose = "the perfect platform") to reach the pop-up's NO | Mr. Snuggles chase; the cold open plays for real; "If Mom won't press leave, I'll make her want to!" → his face fills Mom's screen → she presses leave |
| 12 | ~93 % | **Resolution list**: back to normal, each gag paid off | "Grass is grass. Plastic is not plastic. Mom has one hat again. Dad can put his arms down." Dad: "And I finally made it to the car!" | "Real couch. Real living room. And a face that can frown again." Mom: "Sweetie, you were gone for like an hour." |
| 13 | ~95 % | **"Almost."**: one leftover from the game | "Breakfast, sweetie!" still pops up in a chat bubble | the tutu and the bunny ears came with you |
| 14 | ~97 % | **Comment CTA**: one game word, before the last beat (`lessons.md` rule 4) | "Comment oof if you'd turn the world into Roblox." | "Comment join if you jump into Roblox!" |
| 15 | last 6-10 s | **Loop line**: a system message + the Kid's panic sends the story back to the start | Game: "Update failed. Rolling back to day one." · Kid: "No, no, no! Not day one!" | Game: "You left the game. Rejoin." · Kid: "Mom! No! Don't press rejoin!" |

### 7.4 The cast: who speaks, what, and how (measured)
One voice performer does every part. The narrator's own voice (~160 Hz) also plays Dad, Mom, the mentor and the NPCs. A second, high, pitched-up voice carries most Kid and Game lines.

| Speaker | WORLD: lines / words / pitch | SUCKED: lines / words / pitch | What they say | Emotions (in order of use) |
|---|---|---|---|---|
| **Narrator** | 121 / 811 / 158 Hz | 148 / 709 / 161 Hz | 2nd person "you", present tense; every Day word, rule, list, both CTAs; dry tags after big lines ("Delayed ow.", "Still 99 robux.", "He's seven.", "Feet first.", "Nobody has ever known.") | calm (facts) → excited (escalations, "!") → deadpan (tags) → whispering / soft ("something is wrong", reveals) → curious (the "Your bed?" questions) |
| **Kid** ("you") | 22 / 108 / 324 Hz | 50 / 154 / 374 Hz | first-person reactions to his own body and the world; the careless trigger line; smug one-liners; panicked shouts; the plan; the loop line | excited, confused, nervous, panicked, smug, pleading, whispering (realisations), tired |
| **Mom** | 7 / 24 / 267 Hz | 25 / 85 / 284 Hz | "sweetie" lines (warm words, absurd situation); gets hooked on one Roblox thing (hats, the avatar shop); clueless with the controls; the big scream at the climax | sweet → excited ("Ooh!", "Buy!") → confused → screaming |
| **Dad** | 11 / 47 / 129 Hz | 12 / 28 / 172 Hz | a **running gag in 3-4 stages** with a payoff (walks into a wall "I'm just going to the car" → disconnected → T-pose "I'm fine" → the perfect platform → "I finally made it to the car!"); or an addiction ("Just one more upgrade.") | deadpan denial ("I'm fine."), shocked ("800 Robux?!"), proud, excited |
| **Game** (system voice) | 12 / 53 / ~700 Hz | 3 / 11 / ~870 Hz | Roblox UI messages read flatly, and each is a joke: "Equipped." "You have been disconnected. Reason, idle for 20 minutes." "You do not own this item." "Update complete." "Joining the scariest game on Roblox." "You left the game. Rejoin." | robotic (flat, very high or processed) |
| **Mentor** (Old Noob) | – | 15 / 86 / 138 Hz | explains the rules, calls the hero "kid", one dry joke ("Good luck with the chat filter."), the final goodbye line | chuckling, serious, whispering ("Listen close.") |
| **Side voices** | Teacher NPC (repeats one robotic line twice), Coach, Neighbor ("Ahh!"), Crowd ("Help! No! What do we do?") | – | one line each, for a gag | robotic-cheerful, screaming, panicked |
| **Silent characters** | the bully, the lemonade customer, the mouse cursor (the owner) | XXProGamerXX, Mr. Snuggles | shown only; the narrator describes them | – |

**Voice contrast for our voice tool:**
- Kid: about +12 semitones over the narrator.
- Mom: +9 semitones.
- Dad / mentor: −2 to −3 semitones.
- Game: very high and flat, or a robot effect.

### 7.5 Joke techniques (use them, with our own content)
- **Two-beat joke**: a setup, then a 1-4 word tag. "You look at your hands. They're blocks." · "Dad checks his wallet. Zero Robux. He's been a free player his whole life."
- **Question-answer fragments**: "Your bed? Plastic. Your floor? Covered in tiny little studs." · "Infinite sprinkles? 400."
- **Rule of three, the third one absurd**: "the roof, then the neighbor's roof, then a passing bird." · "And spins it. And spins it. And spins it!"
- **A Roblox mechanic as a real-life joke**: daily reward alarm, toothbrush in the hotbar, fall damage on the stairs, click to eat, idle disconnect, respawn on clean sheets, game passes, T-pose, lag/ping, an unanchored part falling, copy-paste, chat filter hashtags, emotes as faces, everybody jumping, server shutdown, rejoin.
- **Word-by-word dialogue**: "Mom. Stop. Spinning. The sky." · "Dad. Press. Leave." → the filter: "Dad. Press. Hashtag, hashtag, hashtag."
- **A misread reveal**: the LEAVE letters seen from the back → "E-V-A-E-L. … Evel! What a pretty name for a castle!"
- **Running gags in 3-4 stages, all paid off in the resolution** (Dad + the car, Mom + the hats, the chat filter, the tutu).
- **Callbacks in the climax**: the solution is built from earlier gags (the tower of characters, the pop-up's NO, the cold-open line).
- **Time contrast**: "And here, a whole night goes by. Out there, Dad's been playing for six minutes."

### 7.6 Writing a long script (rules)
Use the user's format (section 3): `Speaker: [emotion] text`, a blank line between speaker turns, and **a name before every line**.

1. **Speaker names:** Narrator, Kid, Mom, Dad, Game, and side characters by role (Teacher NPC, Old Noob, Coach, Crowd, Neighbor…).
   - Every Roblox message is its own `Game:` line with `[robotic]`.
2. **Length:** 1,000-1,150 words.
   - 5 or 7 days of 110-150 words each; the last day 200-250 words.
   - The intro (beats 1-5) is 60-105 words.
3. **Characters:** 30-35 % of sentences are character lines, so most turns are 1-3 sentences long.
   - Every day has at least 2 characters and 4-10 character lines.
   - Dad and Mom each get one running gag that returns 3-4 times.
4. **Emotions:**
   - Use the section 4 tags.
   - Add the long-video tags: `[nervous]`, `[panicked]`, `[smug]`, `[scared]`, `[proud]`, `[tired]`, `[dizzy]`, `[serious]`, `[sneaky]`, `[screaming]`, `[robotic]`.
   - Change the tag whenever the feeling changes.
5. **Pauses:**
   - `[break]` between sentences.
   - `[pause]` after a punch line.
   - `[long pause]` before every "Day N" and each CTA.
   - At most one dramatic silence (the transformation).
6. **Analytics rules still apply** (`lessons.md`):
   - The hook question comes in ≤ 4 s and the stakes by ~11 s.
   - The subscribe CTA comes right after a cliff-hanger and right before a turn.
   - The comment CTA comes before the loop line.
   - The last spoken line loops into the start.
7. **What to give when asked for a long script:**
   - the full script;
   - then a 1-line speaker list with the line count per speaker;
   - the Day map (Day → domain → main gag);
   - the estimated length (words ÷ 130 per minute).

## 8. Analysing a voice the user sends (who speaks, what, and how)
When the user sends an audio (+ SRT) and asks how many characters there are, who says what, and with which tone or emotion:

1. **If it has music** (a finished video), separate the voice first:
   `python3 analysis/separate.py <audio> analysis/models/UVR-MDX-NET-Inst_HQ_3.onnx output/<name>/sep`.
   About 8 minutes for an 8-minute file.
2. **First pass:** `python3 analysis/voice_cast.py <voice> <subs.srt> output/<name>/auto`. It works sentence by sentence:
   - **time:** a sentence boundary inside a cue moves to the quietest point;
   - **pitch:** median and range;
   - **loudness, speed** and breathiness;
   - **audio voice:** voices are clustered only when they are clearly apart (silhouette ≥ 0.3); usually one performer does every part;
   - **speaker:** from the words: narration vs first-person and reaction lines, "sweetie" → Mom, "Mom," → Kid, game / UI messages → Game, the protagonist ("you" → Kid, or the named hero);
   - **emotion:** each line compared with its own speaker's average, plus punctuation.
3. **Hand-check the speakers from the story.** The first pass got 77 % (WORLD) and 75 % (SUCKED) of the sentences right, and 83-91 % on narrator vs character.
   - Write `[[t0, t1, "Speaker"], …]` for every character line.
   - Re-run with `--roles <file>`: the pitch and tone baselines are then per real speaker.
4. **Read `cast.md`** (every line with its numbers) and correct the character emotions by ear and context.
5. **Report in Hinglish:**
   - how many speakers and how many audio voices;
   - each speaker's lines, words, pitch and main tones;
   - the full script in the user's format (`script.txt`);
   - the structure: days, CTAs, pauses.
