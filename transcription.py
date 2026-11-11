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
import numpy as np  # noqa: E402
import pretty_midi  # noqa: E402
import soundfile as sf  # noqa: E402

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
    audio_length: float    # seconds of audio actually transcribed, after trimming
    silence_start: float   # seconds of silence removed from the beginning
    silence_end: float     # seconds of silence removed from the end


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


# Silence detection. Loudness is measured in short frames; a frame counts as sound
# when it is clearly above the recording's own noise floor.
FRAME = 0.05    # seconds per loudness measurement
HOP = 0.025     # seconds between measurements
MIN_RUN = 4     # consecutive loud frames needed to count as sound (ignores clicks under ~50 ms)
START_MARGIN = 0.25   # seconds kept before the first sound
END_MARGIN = 2.0      # seconds kept after the last clear sound, so a fading final chord survives


def find_sound(y: np.ndarray, sr: int) -> tuple[float, float]:
    """Return (start, end) in seconds of the part of a mono signal that is not silence.

    The threshold is 10 dB above the quietest 5 percent of frames (the noise floor).
    As a sanity limit it is never higher than 10 dB below the loudest frame, so a very
    noisy or heavily compressed recording still keeps its music. If nothing is found,
    the whole signal is returned.
    """
    total = len(y) / sr
    frame, hop = int(sr * FRAME), int(sr * HOP)
    if len(y) < frame:
        return 0.0, total
    starts = np.arange(0, len(y) - frame + 1, hop)
    energy = np.concatenate([[0.0], np.cumsum(y.astype(np.float64) ** 2)])
    rms = np.sqrt((energy[starts + frame] - energy[starts]) / frame)
    db = 20 * np.log10(rms + 1e-9)
    heard = db[db > -90]  # ignore digital silence (exact zeros) when estimating the noise floor
    floor = np.percentile(heard, 5) if len(heard) else db.max()
    threshold = min(floor + 10, db.max() - 10)
    loud = (db > threshold).astype(int)
    runs = np.flatnonzero(np.convolve(loud, np.ones(MIN_RUN, dtype=int), "valid") == MIN_RUN)
    if len(runs) == 0:
        return 0.0, total
    start = max(0.0, runs[0] * HOP - START_MARGIN)
    end = min(total, (runs[-1] + MIN_RUN - 1) * HOP + FRAME + END_MARGIN)
    return start, end


def trim_silence(wav: Path) -> tuple[Path, float, float, float]:
    """Cut leading and trailing silence from a WAV file.

    Returns (path to trimmed WAV, seconds cut at start, seconds cut at end, length kept).
    If nothing needs cutting, the original path is returned.
    """
    y, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    y = y.mean(axis=1)
    total = len(y) / sr
    start, end = find_sound(y, sr)
    if start <= 0 and end >= total:
        return wav, 0.0, 0.0, total
    out = Path(tempfile.mkdtemp()) / (wav.stem + "_trimmed.wav")
    sf.write(str(out), y[int(start * sr):int(end * sr)], sr)
    return out, start, total - end, end - start


def transcribe(audio_path: Path, midi_path: Path) -> Transcription:
    """Run Basic Pitch on audio_path, write a MIDI file to midi_path, return the notes.

    Silence at the beginning and end is removed first, so note times count from the
    first sound, not from the start of the file.
    """
    wav = to_wav(audio_path)
    wav, silence_start, silence_end, audio_length = trim_silence(wav)

    started = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):  # the CoreML backend prints debug info
        _, midi_data, events = predict(str(wav), get_model())
    seconds_taken = time.perf_counter() - started

    midi_data.write(str(midi_path))
    notes = sorted(
        (Note(start, end, pitch, amplitude) for start, end, pitch, amplitude, _bends in events),
        key=lambda n: n.start,
    )
    return Transcription(notes, midi_path, seconds_taken, audio_length, silence_start, silence_end)
