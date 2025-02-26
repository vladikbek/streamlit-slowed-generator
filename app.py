import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment
from pydub.effects import normalize
from streamlit_advanced_audio import audix
import base64

st.set_page_config(
    page_title="Slowed & Sped Up Generator",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 Slowed & Sped Up Generator")
st.write("Upload a WAV file to create slowed and sped up versions.")

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

# Function to convert audio bytes to base64 for Audix player
def get_audio_base64(audio_bytes):
    return base64.b64encode(audio_bytes).decode('utf-8')

if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    # Display audio player for the original file
    st.subheader("Original Audio")
    
    # Use Audix for the original audio
    audio_bytes = uploaded_file.getvalue()
    audix(
        audio_bytes=audio_bytes,
        sample_rate=44100,  # Default sample rate, will be overridden by the file
        waveform_color="#1DB954",
        background_color="#F0F2F6",
        time_color="#262730",
        height=120
    )
    
    # Load the audio directly from the uploaded file bytes
    audio_io = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_wav(audio_io)
    
    # Create different speed versions with descriptive names
    speed_versions = {
        "slowed_10": {"factor": 0.9, "suffix": "(SLOWED)", "color": "#1DB954"},
        "slowed_20": {"factor": 0.8, "suffix": "(SUPER SLOWED)", "color": "#2E77D0"},
        "slowed_40": {"factor": 0.6, "suffix": "(ULTRA SLOWED)", "color": "#9C27B0"},
        "sped_up_20": {"factor": 1.2, "suffix": "(SPED UP)", "color": "#FF5722"},
    }
    
    processed_files = {}
    display_names = {}
    
    for name, info in speed_versions.items():
        factor = info["factor"]
        suffix = info["suffix"]
        
        # Change the speed
        if factor < 1:
            # For slowing down
            modified_audio = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * factor)
            })
            modified_audio = modified_audio.set_frame_rate(audio.frame_rate)
        else:
            # For speeding up
            modified_audio = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * factor)
            })
            modified_audio = modified_audio.set_frame_rate(audio.frame_rate)
        
        # Apply clipping to ensure audio doesn't peak above 0dB
        # First normalize to ensure we're using the full dynamic range without clipping
        modified_audio = normalize(modified_audio, headroom=0.1)  # 0.1dB headroom to prevent clipping
        
        # Export the modified audio to bytes
        output_buffer = io.BytesIO()
        modified_audio.export(output_buffer, format="wav")
        processed_files[name] = output_buffer.getvalue()
        
        # Create display name for this version
        display_names[name] = f"{original_filename} {suffix}.wav"
    
    # Display all versions with audio player and download button side by side
    st.subheader("Generated Versions")
    
    # Display each version with Audix player and download button side by side
    for name, data in processed_files.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{display_names[name]}**")
            # Use Audix for each modified version
            audix(
                audio_bytes=data,
                sample_rate=audio.frame_rate,
                waveform_color=speed_versions[name]["color"],
                background_color="#F0F2F6",
                time_color="#262730",
                height=120
            )
        with col2:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            st.download_button(
                label="Download",
                data=data,
                file_name=display_names[name],
                mime="audio/wav"
            )
        st.divider()  # Add a divider between versions
    
    # Create a zip file with all versions
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add all modified versions with their display names (excluding original)
        for name, data in processed_files.items():
            zip_file.writestr(display_names[name], data)
    
    # Full width primary button for downloading all versions
    st.download_button(
        label="Download All Versions",
        data=zip_buffer.getvalue(),
        file_name=f"{original_filename}_all_versions.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary"
    ) 