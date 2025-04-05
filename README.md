# Slowed & Sped Up Generator

A Streamlit web application that allows users to modify the speed of various audio files (WAV, MP3, FLAC, etc.). Create slowed down and sped up versions of your audio files with adjustable settings.

## Features

- Upload various audio file formats (requires ffmpeg for non-WAV).
- Configure speed versions (Slowed, Super Slowed, Ultra Slowed, Sped Up) using checkboxes and sliders in the sidebar.
- Output all versions, including a processed version of the original, in standardized 44.1 kHz, 16-bit WAV format.
- Normalize all output files to 0 dBFS.
- Preview all generated versions in the browser.
- Download individual modified versions.
- Download all generated versions (including processed original) as a single ZIP file.

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

1. Open the application in your web browser.
2. Open the sidebar (if hidden) to configure the speed versions. Use the checkboxes to enable/disable versions and the sliders to adjust the speed factor for each.
3. Upload an audio file using the file uploader.
4. Wait for the processing to complete (progress bar will indicate status). This includes processing the original file and all enabled speed versions.
5. Preview the generated versions (including the processed original) in the "View All Processed Versions" expander.
6. Download individual versions using the respective download buttons or download all versions in a ZIP file using the primary button.

## Requirements

- Python 3.7+
- Streamlit
- Pydub
- ffmpeg (for handling various audio formats)

## License

MIT 