import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment

st.set_page_config(
    page_title="Audio Speed Modifier",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 Audio Speed Modifier")
st.write("Upload a WAV file to create slowed and sped up versions.")

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    # Display audio player for the original file
    st.subheader("Original Audio")
    st.audio(uploaded_file, format="audio/wav")
    
    # Load the audio directly from the uploaded file bytes
    audio_bytes = uploaded_file.getvalue()
    audio_io = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_wav(audio_io)
    
    # Create different speed versions with descriptive names
    speed_versions = {
        "slowed_10": {"factor": 0.9, "suffix": "(SLOWED)"},
        "slowed_20": {"factor": 0.8, "suffix": "(SUPER SLOWED)"},
        "slowed_40": {"factor": 0.6, "suffix": "(ULTRA SLOWED)"},
        "sped_up_20": {"factor": 1.2, "suffix": "(SPED UP)"},
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
        
        # Export the modified audio to bytes
        output_buffer = io.BytesIO()
        modified_audio.export(output_buffer, format="wav")
        processed_files[name] = output_buffer.getvalue()
        
        # Create display name for this version
        display_names[name] = f"{original_filename} {suffix}.wav"
    
    # Display individual download buttons
    st.subheader("Download Individual Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Slowed Versions:")
        st.audio(processed_files["slowed_10"], format="audio/wav")
        st.download_button(
            label=f"Download {display_names['slowed_10']}",
            data=processed_files["slowed_10"],
            file_name=display_names["slowed_10"],
            mime="audio/wav"
        )
        
        st.audio(processed_files["slowed_20"], format="audio/wav")
        st.download_button(
            label=f"Download {display_names['slowed_20']}",
            data=processed_files["slowed_20"],
            file_name=display_names["slowed_20"],
            mime="audio/wav"
        )
        
        st.audio(processed_files["slowed_40"], format="audio/wav")
        st.download_button(
            label=f"Download {display_names['slowed_40']}",
            data=processed_files["slowed_40"],
            file_name=display_names["slowed_40"],
            mime="audio/wav"
        )
    
    with col2:
        st.write("Sped Up Version:")
        st.audio(processed_files["sped_up_20"], format="audio/wav")
        st.download_button(
            label=f"Download {display_names['sped_up_20']}",
            data=processed_files["sped_up_20"],
            file_name=display_names["sped_up_20"],
            mime="audio/wav"
        )
    
    # Create a zip file with all versions
    st.subheader("Download All Versions")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add the original file
        zip_file.writestr(f"{original_filename}.wav", audio_bytes)
        
        # Add all modified versions with their display names
        for name, data in processed_files.items():
            zip_file.writestr(display_names[name], data)
    
    st.download_button(
        label="Download All as ZIP",
        data=zip_buffer.getvalue(),
        file_name=f"{original_filename}_all_versions.zip",
        mime="application/zip"
    ) 