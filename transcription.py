"""Turn a recording into notes and a MIDI file using Basic Pitch.

Used by both the command line script (scripts/transcribe.py) and the website (app.py).
"""

import contextlib
import io
import logging
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.ERROR)  # hide Basic Pitch's backend-selection warnings

from basic_pitch import ICASSP_2022_MODEL_PATH  # noqa: E402
from basic_pitch.inference import Model, predict  # noqa: E402
import pretty_midi  # noqa: E402

_model = None


def get_model() -> Model:
    """Load the model once and keep it. Loading takes a moment; reusing it is free."""
    global _model
    if _model is None:
        _model = Model(ICASSP_2022_MODEL_PATH)
    return _model


@dataclass
class Note:
    start: float      # seconds from the beginning of the recording
    end: float
    pitch: int        # MIDI number, 60 is middle C
    loudness: float   # 0 to 1, Basic Pitch's confidence/amplitude for the note

    @property
    def name(self) -> str:
        return pretty_midi.note_number_to_name(self.pitch)

    @property
    def length(self) -> float:
        return self.end - self.start


@dataclass
class Transcription:
    notes: list[Note]
    midi_path: Path
    seconds_taken: float

    @property
    def audio_length(self) -> float:
        return max((n.end for n in self.notes), default=0.0)


def to_wav(path: Path) -> Path:
    """Basic Pitch reads WAV reliably. Convert anything else first.

    Uses afconvert (built into macOS) or ffmpeg, whichever is available.
    """
    if path.suffix.lower() == ".wav":
        return path
    out = Path(tempfile.mkdtemp()) / (path.stem + ".wav")
    if shutil.which("afconvert"):
        cmd = ["afconvert", "-f", "WAVE", "-d", "LEI16", str(path), str(out)]
    elif shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), str(out)]
    else:
        raise RuntimeError("Only .wav files are supported on this machine (no afconvert or ffmpeg found).")
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def transcribe(audio_path: Path, midi_path: Path) -> Transcription:
    """Run Basic Pitch on audio_path, write a MIDI file to midi_path, return the notes."""
    wav = to_wav(audio_path)

    started = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):  # the CoreML backend prints debug info
        _, midi_data, events = predict(str(wav), get_model())
    seconds_taken = time.perf_counter() - started

    midi_data.write(str(midi_path))
    notes = sorted(
        (Note(start, end, pitch, amplitude) for start, end, pitch, amplitude, _bends in events),
        key=lambda n: n.start,
    )
    return Transcription(notes, midi_path, seconds_taken)
