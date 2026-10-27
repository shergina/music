# Plan

A practice tool for musicians. You bring in music any way you have it, get a version you can actually play, practice it, and see how close you are getting.

Team of five, two to three months. This file is the plan as of 27 October 2026. Update it when a decision changes.

## Who it is for

A beginner or intermediate player practicing alone at home, without a teacher in the room. They play a piece, it sounded off, and they do not know exactly where or why. Everything we build should answer one question: **what should I fix next?**

We start with piano. Voice is the second instrument. Guitar is out of scope for now.

## What it does

1. **Input.** Record from a microphone (an instrument or a person humming), play on a MIDI keyboard, or import a MIDI or MusicXML file.
2. **Transcribe.** Audio becomes a list of notes, each with a pitch, a start time, a length and a loudness.
3. **Clean up.** Snap notes to the beat, merge fragments, drop tiny notes, detect chords.
4. **Rate.** A difficulty model scores the piece, for example level 4 out of 5.
5. **Simplify.** The user picks a target level. A rules engine reduces the piece step by step, asking the rater after each step, and stops when it reaches the target. The result still sounds like the song.
6. **Show.** Score view, piano roll, playback with a moving cursor, export to MIDI, MusicXML and PDF.
7. **Practice.** The user records a take. We compare it to the reference and show where it differs.

## The practice feature

This is the heart of the product. The reference is the score the user made in the tool, or a MIDI file they imported. Comparing to a recording of a famous player is the same code but needs a legal source for the recording, so it comes later.

### How a comparison works

1. **Turn both recordings into notes.** Reference and student take both go through transcription.
2. **Line them up.** The student will not play at the same speed as the reference. Dynamic time warping stretches the student's timeline so each note sits next to the note it was trying to be.
3. **Check the notes.** Same pitch as the matched note: correct. Different pitch: wrong note. Reference note with no match: missed. Student note with no match: extra.
4. **Check tempo and rhythm.** The alignment tells us how much each bar was stretched. A bar that took 20 percent longer means the student slowed down there. Within a bar, the gaps between notes tell us about rhythm.
5. **Show it.** Reference on top, student below, mistakes highlighted, a tempo line underneath, and one plain sentence: "You slowed down in bars 9 to 12 and missed the F sharp in bar 11."

Steps 1 to 5 need no training. They work on day one.

### Features we are committing to

| # | Feature | What it does |
|---|---|---|
| 1 | **Compare a take to the reference** | Tempo, rhythm, and wrong, missed or extra notes, shown bar by bar. |
| 2 | **Focus on a section and slow down** | Pick bars, loop them at a slower tempo with the reference playing along, speed up as the player gets it right. Playing slower on purpose is never counted as a mistake. |
| 3 | **Compare to the last take** | "Three fewer mistakes than yesterday." Progress against yourself, not just distance from the reference. |
| 4 | **Show the hardest spot** | Find the bar with the most problems and point at it. Do not list thirty errors. |
| 5 | **Turn off tempo checking** | While learning the notes, speed does not matter. The user can switch tempo and rhythm checks off and back on. |
| 6 | **Set tolerance** | How late or early a note can be before it counts. Loose by default for beginners, tighter as the user levels up. |

### Later, once the above works

- Dynamics: did they play loud and soft in the right places. Useful for intermediate players, noise for beginners.
- Compare against a famous performance, once we have a legal reference source.
- A learned overall similarity score (see Siamese network below) alongside the classical comparison.
- Voice as an instrument. A singer slightly flat is not "wrong", so we measure how far off instead of right or wrong.

## Where neural networks are used and where they are not

Rule of thumb: audio is the network's territory, symbols (notes) are the algorithm's territory.

| Problem | Approach | Why |
|---|---|---|
| Audio to notes | Pretrained network, fine-tuned by us | Classical methods fail on overtones and chords. This is the one place a network is the only option. |
| Beat tracking, chord detection | Classical signal processing | Good enough for melodies and simple harmony, easy to debug. |
| Difficulty rating | Small network trained by us | Difficulty has too many interacting factors for a hand-written formula. Small data, so a small model. |
| Simplify | Rules, judged by the difficulty model | We know exactly what we want, and there is no dataset of expert simplifications to learn from. |
| Fingering, hand split | Dynamic programming | Exact optimization beats learning here. |
| Performance alignment | Dynamic time warping | Textbook tool, exactly right for this. |
| Overall similarity score | Siamese network, stretch goal | Learns what "sounds close" means from pairs. Classical version explains, network judges. |

### The three training projects

Each has a baseline to beat, a public metric, and a fallback so the product never depends on it.

**1. Fine-tune a transcription model on piano.** Start from Basic Pitch or Onsets and Frames. Train on MAESTRO (about 200 hours of piano audio with exact MIDI). Measure note F1 on onset and pitch with mir_eval. Report the pretrained model's score before and after. Needs a few GPU hours (Colab or student cloud credits). Fallback: the pretrained model as is.

**2. Train a difficulty rater from scratch.** Features per piece: notes per second, average and max interval, pitch range, notes sounding at once, rhythmic variety, hand span, key, tempo. Small network over those features. Data: Can I Play It dataset, Henle grades paired with public domain MIDI, ABRSM and RCM syllabuses, Mikrokosmos, plus a few hundred pieces we label ourselves using a written definition of each level, two raters per piece. Baseline: a plain regression on the same features. Fallback: fixed number of simplification steps per level.

**3. Siamese similarity for performances.** Two copies of one network map a short window of a performance to a vector; distance between vectors is similarity. Training pairs come free: take clean MIDI performances and make degraded copies (shifted timing, dropped notes, flattened dynamics, wrong notes), so the label is known. Add a few hundred human-rated pairs to calibrate. Read about contrastive and triplet loss first. Fallback: dynamic time warping distance.

## Team lanes

| Lane | Owns | Training project | Shows at the end |
|---|---|---|---|
| Audio and transcription | microphone and MIDI capture, Basic Pitch integration, beat and chord detection, note cleanup | fine-tune transcription | a recording goes in, clean notes come out |
| Arrangement engine | simplify, transpose, hand split, fingering, accompaniment | difficulty rater | one piece at three levels that all sound like the song |
| Notation and playback | score rendering, piano roll, playback, export | none | a printable score of anything the engine produces |
| Practice and feedback | take recording, alignment, mistakes, tempo line, loops, progress | Siamese similarity | the practice mode as a standalone demo |
| Product and platform | app shell, accounts, library, sharing, mobile layout, accessibility, user testing | none | a thing people can sign up for and use |

The seams between lanes are data formats. Agree on these in week one so every lane can build against fixtures:

- A **note list**: pitch, onset, duration, velocity.
- A **chord list**: root, quality, start, end.
- **MusicXML** for anything that touches notation.
- A **comparison result**: per bar, the stretch factor, and a list of wrong, missed and extra notes.

## Milestones

1. **Weeks 1 to 2. Thinnest path end to end.** Hum, see notes, hear them back, download a MIDI file. Every lane plugs into this.
2. **Weeks 3 to 5. Practice mode, single melody.** Record a take, align, show mistakes and tempo line. Features 1, 4, 5 and 6.
3. **Weeks 6 to 8. Practice loop and progress.** Features 2 and 3. Difficulty rater v1. Simplify v1.
4. **Weeks 9 to 11. Two hands.** Simplify, difficulty and score view for full piano arrangements. Fine-tuned transcription model deployed.
5. **Week 12. Polish and test.** Real beginners use it. Siamese score if there is time.

## Decisions so far

- Piano first. Voice second. Guitar not now.
- Single melody line first, two hands as a later milestone.
- Do not build transcription from scratch. Fine-tune a pretrained model.
- Do not write a notation engraver. Use a library.
- Reference for practice is the user's own score or an imported MIDI, not a copyrighted recording.
- Compare against your own past takes, not only against the reference.
- The difficulty rater must be fast (milliseconds) because the simplifier calls it many times per piece.
- No real-time collaborative editing.

## Open questions

- Which notation library. Candidates: VexFlow, OpenSheetMusicDisplay.
- Browser only, or a server for the heavier models.
- Written definitions for difficulty levels 1 to 5.
- Where GPU time comes from for fine-tuning.
- How to handle a singer who is slightly flat across the whole piece (transpose the reference, or report it).
