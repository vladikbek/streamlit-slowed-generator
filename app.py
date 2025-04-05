import streamlit as st
import os
import zipfile
import io
import subprocess
from pydub import AudioSegment
from pydub.effects import normalize

# Check if ffmpeg is installed
def is_tool_installed(name):
    try:
        subprocess.check_output([name, "-version"], stderr=subprocess.STDOUT)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# Set page config
st.set_page_config(
    page_title="Slowed & Sped Up Generator",
    page_icon="💿",
    layout="centered"
)

st.title("💿 Slowed & Sped Up Generator")

# Check for ffmpeg dependency
if not is_tool_installed("ffmpeg"):
    st.error("⚠️ FFmpeg is not installed. This app requires FFmpeg to process audio files.")
    st.info("""
    ### How to install FFmpeg:
    
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
    
    After installing, restart this application.
    """)
    st.stop()

# Allow both MP3 and WAV files
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

if uploaded_file is not None:
    try:
        # Get the original filename without extension
        original_filename = os.path.splitext(uploaded_file.name)[0]
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Load the audio based on file type
        audio_bytes = uploaded_file.getvalue()
        audio_io = io.BytesIO(audio_bytes)
        
        if file_extension == '.wav':
            audio = AudioSegment.from_wav(audio_io)
        else:  # mp3
            audio = AudioSegment.from_mp3(audio_io)
        
        # Standardize to 44.1 kHz 16-bit WAV
        audio = audio.set_frame_rate(44100).set_sample_width(2)
        
        # Sidebar for preset customization
        with st.sidebar:
            st.header("Speed Presets")
            st.caption("Customize your speed factors")
            
            # Default presets that user can modify
            slow_10 = st.slider("Slowed", 0.5, 0.95, 0.9, 0.05, format="%.2f")
            slow_20 = st.slider("Super Slowed", 0.3, 0.85, 0.8, 0.05, format="%.2f")
            slow_40 = st.slider("Ultra Slowed", 0.1, 0.7, 0.6, 0.05, format="%.2f")
            speed_up = st.slider("Sped Up", 1.05, 2.0, 1.2, 0.05, format="%.2f")
        
        # Create different speed versions with user-defined factors
        speed_versions = {
            "original": {"factor": 1.0, "suffix": "ORIGINAL"},
            "slowed_10": {"factor": slow_10, "suffix": "SLOWED"},
            "slowed_20": {"factor": slow_20, "suffix": "SUPER SLOWED"},
            "slowed_40": {"factor": slow_40, "suffix": "ULTRA SLOWED"},
            "sped_up_20": {"factor": speed_up, "suffix": "SPED UP"},
        }
        
        processed_files = {}
        display_names = {}
        
        for name, info in speed_versions.items():
            factor = info["factor"]
            suffix = info["suffix"]
            
            if name == "original":
                # For the original version, just normalize it
                modified_audio = audio
            elif factor < 1:
                # For slowing down
                modified_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * factor)
                })
                modified_audio = modified_audio.set_frame_rate(44100)
            else:
                # For speeding up
                modified_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * factor)
                })
                modified_audio = modified_audio.set_frame_rate(44100)
            
            # Apply normalization to ensure audio doesn't peak above 0dB
            modified_audio = normalize(modified_audio, headroom=0.1)  # 0.1dB headroom to prevent clipping
            
            # Export the modified audio to bytes as 44.1 kHz 16-bit WAV
            output_buffer = io.BytesIO()
            # Use simpler parameters to avoid issues
            modified_audio.export(output_buffer, format="wav")
            processed_files[name] = output_buffer.getvalue()
            
            # Create display name for this version
            if name == "original":
                display_names[name] = f"{original_filename}.wav"
            else:
                display_names[name] = f"{original_filename} ({suffix}).wav"
        
        # Create a zip file with all versions
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add all modified versions with their display names
            for name, data in processed_files.items():
                zip_file.writestr(display_names[name], data)
        
        # Full width primary button for downloading all versions right after upload
        st.download_button(
            label="Download All Versions",
            data=zip_buffer.getvalue(),
            file_name=f"{original_filename}_all_versions.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )
        
        # Display all versions with audio player
        with st.expander("View All Versions", expanded=True):
            # Display each version with audio player
            for name, data in processed_files.items():
                if name == "original":
                    st.subheader("ORIGINAL")
                else:
                    speed_factor = speed_versions[name]["factor"]
                    st.subheader(f"{speed_versions[name]['suffix']} ({speed_factor}x)")
                st.audio(data, format="audio/wav")
                st.divider()  # Add a divider between versions
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        st.info("Make sure you have FFmpeg installed correctly and try again.") 