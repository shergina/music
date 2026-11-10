"""A small website: upload two recordings, get the notes and a MIDI file for each.

Run it with:
    .venv/bin/python app.py
then open http://127.0.0.1:8000
"""

import uuid
from pathlib import Path

from flask import Flask, abort, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from transcription import get_model, transcribe

ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"  # one folder per job; ignored by git
UPLOADS.mkdir(exist_ok=True)

# Each recording the user uploads: form field name, label shown on the page.
RECORDINGS = [
    ("student", "Your recording"),
    ("reference", "Ideal pianist's recording"),
]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB per request


@app.get("/")
def index():
    return render_template("index.html", recordings=RECORDINGS)


@app.post("/transcribe")
def do_transcribe():
    job = uuid.uuid4().hex[:8]
    folder = UPLOADS / job
    folder.mkdir()

    results = []
    for field, label in RECORDINGS:
        upload = request.files.get(field)
        if upload is None or not upload.filename:
            abort(400, f"Please choose a file for: {label}")
        suffix = Path(secure_filename(upload.filename)).suffix.lower() or ".wav"
        audio_path = folder / f"{field}{suffix}"
        upload.save(audio_path)

        try:
            result = transcribe(audio_path, folder / f"{field}.mid")
        except Exception as exc:  # unreadable file, unsupported format, etc.
            abort(400, f"Could not transcribe {label} ({upload.filename}): {exc}")

        results.append(
            {
                "label": label,
                "filename": upload.filename,
                "midi_url": f"/uploads/{job}/{field}.mid",
                "result": result,
            }
        )

    return render_template("result.html", job=job, results=results)


@app.get("/uploads/<job>/<name>")
def download(job: str, name: str):
    return send_from_directory(UPLOADS / job, name, as_attachment=True)


if __name__ == "__main__":
    get_model()  # load once at startup so the first upload is not slow
    app.run(host="127.0.0.1", port=8000, debug=False)
