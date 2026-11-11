"""Run Basic Pitch on a recording and print the notes it finds.

Usage:
    .venv/bin/python scripts/transcribe.py path/to/recording.wav

Accepts .wav directly. Other formats (.m4a from Voice Memos or QuickTime, .mp3,
.aiff) are converted to .wav first. Writes a MIDI file next to the input with
the same name and a .mid extension.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transcription import get_model, transcribe  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"File not found: {src}")

    started = time.perf_counter()
    get_model()
    load_time = time.perf_counter() - started

    result = transcribe(src, src.with_suffix(".mid"))

    print(f"{'start':>7}  {'length':>7}  {'note':<5} {'midi':>4}  {'loud':>5}")
    for n in result.notes:
        print(f"{n.start:7.2f}  {n.length:7.2f}  {n.name:<5} {n.pitch:4d}  {n.loudness:5.2f}")

    print()
    print(f"{len(result.notes)} notes found in {result.audio_length:.1f} s of audio")
    print(f"silence removed: {result.silence_start:.2f} s at the start, {result.silence_end:.2f} s at the end")
    print(f"model load {load_time:.1f} s, transcription {result.seconds_taken:.1f} s")
    print(f"MIDI written to {result.midi_path}")


if __name__ == "__main__":
    main()
