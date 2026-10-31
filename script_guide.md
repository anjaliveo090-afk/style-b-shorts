# Script guide: titles, scripts, emotions and silent parts (Style B)

This guide was learned from 6 reference videos (~50-56 s each):
- What If Your MOM Started Playing Roblox
- What If MOM Gave You 10 Seconds of Roblox
- What If Your DAD Became the NOOB KING
- What If You Got 1 ROBUX Every Time You Blinked
- What If You HACKED Roblox
- the robux10 voice the user made

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
| 1 | 0-2.5 s | **Hook**: the title as a question | Narrator | curious | States the absurd idea | "What if your dad became the Noob King?" |
| 2 | 2.5-7 s | **Setup**: a quick exchange or a cool line | a character (or the narrator) | pleading / smug / confident / whispering | Shows the characters and the conflict | kid begs dad to change his avatar, dad: "Nope."; "Watch this."; "I'm in!" |
| 3 | 7-12 s | **Chapter 1**: the first small, funny result | Narrator + a 1-line character reaction | excited / chuckling | The power works, clumsily | can't even jump; blink → DING, it's real |
| 4 | 12-17 s | **Chapter 2**: a surprising escalation | Narrator | excited / gasping | Bigger and stranger | a golden crown drops; /GIANT |
| 5 | 17-23 s | **Chapter 3**: a huge number | Narrator | excited, emphasis on the number | 1,000,000 / trillion / everything free | "One million noobs join his army" |
| 6 | 23-26 s | **Chapter 4**: it goes public | Narrator | excited | The whole server or class sees it | take over every obby; everyone's staring |
| 7 | 26-29 s | **CTA**: "Everyone who subscribes gets ___" (always tied to the power) | Narrator | cheerful | A subscribe button gets pressed on screen | gets ADMIN / joins the noob army / one free blink |
| 8 | 29-35 s | **Chapter 5 = the conflict**: mom or dad steps in | Narrator ("Mom says…") + a character | soft → suspicious / angry | The authority figure arrives | "Tablet. Off. NOW."; "Staring contest, sweetie." |
| 9 | 35-42 s | **Showdown**: the power vs the parent | the characters | pleading / confident / shocked | One clever move each | freeze mom; "Kneel before the King!" |
| 10 | 42-47 s | **Punishment**: everything goes to zero | Narrator | deadpan → sad | The loss, item by item | "Your Robux… Zero."; "Pet, gone."; turns into a noob |
| 11 | 47-49 s | **The parent's sweet ending line** | Mom / Dad | sweet / smug | Irony | "Bedtime, sweetie."; "No more Roblox, sweetie." |
| 12 | 49-52 s | **Twist**: "But then…" one more turn | Narrator | whispering → excited | Opens a new problem | the game updated…; mom forgot one thing… |
| 13 | 50-53 s | **Comment CTA** with ONE keyword | Narrator | cheerful | "Comment HACK if you'd…" | the keyword is the title's power word |
| 14 | 53-56 s | **Loop line**: leads back into the hook | a character | confused / sneaky | Ends mid-action, so the video restarts | "Slash… REWIND!"; "Wait, which button goes back?" |

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

**The pattern:**
- **The kid reacts in the first person** to his own wins ("It's real!", "100 Robux!").
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
