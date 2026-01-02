# Slowed Generator

A simple Streamlit app that takes an uploaded audio track and creates multiple slowed/sped‑up versions. You can tweak versions by speed (%) or pitch (semitones) and download everything as a single zip.

## Features
- Preset slowed/sped‑up variants with per‑preset enable/disable
- Two adjustment modes: speed percentage or pitch semitones
- Optional inclusion of a normalized original
- WAV output (44.1 kHz, 16‑bit) + one‑click zip download
- Supports common input formats (wav, mp3, flac, ogg, m4a, aac)

## Requirements
- Python 3.9+
- ffmpeg (required by pydub for decoding)

On Debian/Ubuntu:
```bash
sudo apt-get install ffmpeg
```

For Streamlit Cloud, `packages.txt` already includes `ffmpeg`.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```

## Usage
1. Upload a track.
2. Choose adjustment mode and enable the presets you want in the sidebar.
3. Click **Start Processing**.
4. Download individual versions or the full zip.

## Notes
- Output filenames include the preset label.
- Audio is normalized to 0 dB headroom for consistent loudness.
