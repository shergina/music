# music

A practice tool for musicians. Record yourself playing a piece, compare it to a reference recording, and see exactly where your take differs.

Read [PLAN.md](PLAN.md) for the core requirements and post-MVP features.

## Setup

Needs Python 3.10 or newer. On a Mac, non-WAV recordings are converted with the built-in `afconvert`; elsewhere install `ffmpeg`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run the website

```bash
.venv/bin/python app.py
```

Then open <http://127.0.0.1:8000>. Upload your recording and the ideal pianist's recording, and you get the notes and a MIDI file for each. Uploaded files and results land in `uploads/`, which git ignores.

## Transcribe one file from the command line

```bash
.venv/bin/python scripts/transcribe.py path/to/recording.m4a
```

Prints every note found and writes a `.mid` file next to the recording.

## Layout

- `transcription.py` turns a recording into notes and a MIDI file with Basic Pitch. Everything else calls this.
- `app.py` and `templates/` are the website.
- `scripts/transcribe.py` is the command line version.
