# Slowed & Sped Up Generator

A Streamlit web application that allows users to modify the speed of WAV audio files. Create slowed down and sped up versions of your audio files with ease.

## Features

- Upload WAV audio files
- Create multiple speed variations:
  - 90% speed (Slowed)
  - 80% speed (Super Slowed)
  - 60% speed (Ultra Slowed)
  - 120% speed (Sped Up)
- Preview all versions in the browser
- Download individual modified versions
- Download all versions as a ZIP file

## Installation

1. Clone this repository:
```bash
git clone https://github.com/vladikbek/streamlit-slowed-spedup.git
cd streamlit-slowed-spedup
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser
2. Upload a WAV file using the file uploader
3. Listen to the preview of original and modified versions
4. Download individual versions or get all versions in a ZIP file

## Requirements

- Python 3.6+
- Streamlit
- PyDub

## License

MIT 