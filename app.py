import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment
from pydub.effects import normalize

st.set_page_config(
    page_title="SLOWED & SPED UP GENERATOR",
    page_icon="💀",
    layout="centered"
)

st.title("💀 Slowed & Sped Up Generator")
st.write("Upload a WAV file to create slowed and sped up versions.")

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    # Load the audio directly from the uploaded file bytes
    audio_bytes = uploaded_file.getvalue()
    audio_io = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_wav(audio_io)
    
    # Create different speed versions with descriptive names
    speed_versions = {
        "slowed_10": {"factor": 0.9, "suffix": "SLOWED"},
        "slowed_20": {"factor": 0.8, "suffix": "SUPER SLOWED"},
        "slowed_40": {"factor": 0.6, "suffix": "ULTRA SLOWED"},
        "sped_up_20": {"factor": 1.2, "suffix": "SPED UP"},
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
        display_names[name] = f"{original_filename} ({suffix}).wav"
    
    # Create a zip file with all versions
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add all modified versions with their display names (excluding original)
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
    
    # Display all versions with audio player and download button side by side in an expander
    with st.expander("View All Versions"):
        # Display each version with audio player and download button side by side
        for name, data in processed_files.items():
            st.subheader(f"{speed_versions[name]['suffix']}")
            st.audio(data, format="audio/wav")
            st.divider()  # Add a divider between versions 