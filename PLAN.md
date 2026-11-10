# Plan

A practice tool for musicians. Record yourself playing a piece, compare it to a reference recording of a professional musician, and see exactly where your take differs.

This file is the plan as of 10 November 2026. Update it when a decision changes.

## Who it is for

A beginner or intermediate player practicing alone at home, without a teacher in the room. They play a piece, it sounded off, and they do not know exactly where or why. Everything we build should answer one question: **what should I fix next?**

We start with piano.

## How it works

1. The user has two recordings: the reference (a professional musician playing the piece) and their own take.
2. Both go through Basic Pitch and become MIDI.
3. We align the two recordings and compare them note by note and bar by bar.
4. The user gets an overall percentage score and a breakdown by notes, rhythm, dynamics and tempo. They control the error thresholds and how much each metric counts toward the overall score.

## Core requirements (P0)

These four are the MVP. All of them must work.

| Feature | Description | Success criteria | Testing approach |
|---|---|---|---|
| **Creating an account** | Creating a user name and connecting it to an email. The user will be able to access their data between sessions by logging in. | Users are able to make accounts and save their data. | Create test users with different data and see if everything works across sessions. |
| **Converting from audio to MIDI** | Taking the recording from the professional musician and the one from the learner and converting both to MIDI. Using Basic Pitch (Spotify's free, open source library), we get the notes for the recordings and a MIDI file. | When we record someone playing the piano, at least 80% of notes are found correctly. The conversion should also take a reasonable amount of time (under 10 seconds?). | We will record William playing the piano and then check whether the notes he played were transcribed correctly. |
| **Percentage comparison between original audio and user's recording** | The user gets a score of how close their recording is to the recording of a professional musician playing. The tool lets the user set a weight for each metric, and the overall score is composed from all the subscores combined. | 1) A recording compared to itself receives a perfect score. 2) The lower the accuracy, the worse the score. 3) The score should change at a reasonable rate. | 1) Compare a recording to itself. 2) Upload recordings of different accuracies and check whether the tool gives scores that are accurate relative to one another. |
| **Breakdown of accuracy** | Metrics on how accurate the user's notes, rhythm, dynamics and tempo are throughout the song. Assign an error score to each measure for each of these metrics. For notes, each note gets "correct", "wrong" or "missed". For rhythm, each note gets a value for how early or late it was in milliseconds. For tempo, a stretch factor per bar. The user can set a threshold for how much error is allowed before it counts as an error. | 1) A recording compared to itself receives a perfect score in each category. 2) The lower the accuracy, the worse the score in each category. | 1) Compare a recording to itself. 2) Upload recordings with different accuracies in different metrics and check whether the tool gives scores for each metric that are accurate relative to one another. |

## Post-MVP features (P1 to P4)

We build these if there is time. The priority numbers are placeholders; the order is not set yet.

| Priority | Feature | Description |
|---|---|---|
| P1 | **Practice one section of the song** | The user chooses a section of the original audio to focus on. They upload just that section and get comparison metrics for it. They can also choose to play that part slower. |
| P2 | **Point out the parts of the song the user needs to work on most** | Using the per-measure error scores, find the run of consecutive measures (about 15% of the song) where the error is highest. |
| P3 | **Make the notes from a recording easier to play** | Replace some notes with ones that sound the same but are easier to reach on the piano, so the user does not have to move their hands as much. |
| P4 | **iOS app** | An iOS version of the website, published on the App Store. |

## Data formats

The seams between features are data formats. Agree on these first so every part can be built and tested against fixtures without a microphone.

- A **note list**: pitch, onset, duration, velocity. This is what Basic Pitch produces and what the comparison consumes.
- A **comparison result**: per bar, the stretch factor and the list of wrong, missed and extra notes; per note, how early or late it was in milliseconds; per metric, an error score per bar.

## Decisions so far

- Piano first.
- Do not build transcription from scratch. Use Basic Pitch as is.
- The reference is a recording of a professional musician playing the piece. It goes through the same audio-to-MIDI step as the student's take.
- The user controls the error thresholds and the weight of each metric in the overall score.
- Website first. An iOS app is post-MVP.

## Open questions

- Browser only, or a server for Basic Pitch and the comparison.
- The target time for transcription. The plan says under 10 seconds, with a question mark.
- How the subscores combine into the overall score, and what "changes at a reasonable rate" means in numbers.
- The order of the post-MVP features.
