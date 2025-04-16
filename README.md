# 🎧 Audio Tools

A Streamlit web application featuring tools for audio manipulation.

## Features

This multi-page application provides the following tools (selectable from the sidebar):

**1. Slowed & Sped Up Generator:**
- Upload a single audio file (various formats supported via ffmpeg).
- Configure speed versions (Slowed, Super Slowed, Ultra Slowed, Sped Up, Super Sped Up) using checkboxes and sliders in the sidebar.
- Generates processed versions (including a processed original) in standardized 44.1 kHz, 16-bit WAV format.
- Normalizes all output files to 0 dBFS.
- Previews all generated versions.
- Download individual versions or all versions as a single ZIP file.

**2. Audio Converter:**
- Upload multiple audio files simultaneously (various formats supported via ffmpeg).
- Converts all uploaded files to standardized 44.1 kHz, 16-bit WAV format.
- Normalizes all output files to 0 dBFS.
- Previews all converted files.
- Download individual converted files or all converted files as a single ZIP file.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/vladikbek/streamlit-slowed-spedup.git
cd streamlit-slowed-spedup
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. **Install ffmpeg**: Pydub relies on ffmpeg for handling various audio formats. Install it using your system's package manager.
   - On Debian/Ubuntu: `sudo apt update && sudo apt install ffmpeg`
   - On macOS (using Homebrew): `brew install ffmpeg`
   - On Windows: Download from the [official ffmpeg site](https://ffmpeg.org/download.html) and add it to your system's PATH.
   *(Note: For Streamlit Community Cloud deployment, add `ffmpeg` to your `packages.txt` file.)*

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser (`streamlit run app.py`).
2. Select the desired tool ("Slowed & Sped Up Generator" or "Audio Converter") from the sidebar.
3. Follow the instructions on the selected page:
    - **Generator:** Configure presets in the sidebar, upload a single file, wait for processing, preview, and download.
    - **Converter:** Upload one or more files, wait for processing, preview, and download.

## Requirements

- Python 3.7+
- Streamlit
- Pydub
- ffmpeg (for handling various audio formats)

## License

MIT 