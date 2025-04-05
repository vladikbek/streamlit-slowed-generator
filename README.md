# Slowed & Sped Up Generator

A Streamlit app that allows you to create slowed and sped up versions of audio files, with customizable speed factors and standardized high-quality output.

## Features

- Upload MP3 or WAV files in any format or bitrate
- Standardized output to 44.1 kHz 16-bit WAV format
- Customizable speed presets
- Normalized audio to avoid clipping
- Download all versions in a single ZIP file

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/vladikbek/streamlit-slowed-spedup.git
   cd streamlit-slowed-spedup
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg (system dependency):

   **Ubuntu/Debian:**
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

   **macOS (using Homebrew):**
   ```
   brew install ffmpeg
   ```

   **Windows (using Chocolatey):**
   ```
   choco install ffmpeg
   ```

   Or download from [FFmpeg's official website](https://ffmpeg.org/download.html)

## Usage

1. Run the app:
   ```
   streamlit run app.py
   ```

2. Upload an audio file (MP3 or WAV)

3. Use the sliders in the sidebar to customize speed factors

4. Preview the results and download all versions

## Troubleshooting

If you see an error about missing `ffmpeg` or `ffprobe`, make sure FFmpeg is properly installed on your system and available in your PATH. 