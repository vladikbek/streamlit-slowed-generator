import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment
from pydub.effects import normalize
from streamlit_advanced_audio import audix, WaveSurferOptions

st.set_page_config(
    page_title="Slowed & Sped Up Generator",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 Slowed & Sped Up Generator")
st.write("Upload a WAV file to create slowed and sped up versions.")

# Define custom wavesurfer options for better visualization
original_options = WaveSurferOptions(
    wave_color="#4285F4",
    progress_color="#DB4437",
    height=80
)

slowed_options = WaveSurferOptions(
    wave_color="#0F9D58", 
    progress_color="#F4B400",
    height=80
)

sped_up_options = WaveSurferOptions(
    wave_color="#DB4437",
    progress_color="#4285F4",
    height=80
)

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    # Display audio player for the original file
    st.subheader("Original Audio")
    
    # Save the uploaded file temporarily to use with audix
    temp_original_path = "temp_original.wav"
    with open(temp_original_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Display original audio with audix
    audix(temp_original_path, wavesurfer_options=original_options)
    
    # Load the audio directly from the uploaded file bytes
    audio_bytes = uploaded_file.getvalue()
    audio_io = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_wav(audio_io)
    
    # Create different speed versions with descriptive names
    speed_versions = {
        "slowed_10": {"factor": 0.9, "suffix": "(SLOWED)", "options": slowed_options},
        "slowed_20": {"factor": 0.8, "suffix": "(SUPER SLOWED)", "options": slowed_options},
        "slowed_40": {"factor": 0.6, "suffix": "(ULTRA SLOWED)", "options": slowed_options},
        "sped_up_20": {"factor": 1.2, "suffix": "(SPED UP)", "options": sped_up_options},
    }
    
    processed_files = {}
    display_names = {}
    temp_file_paths = {}
    
    for name, info in speed_versions.items():
        factor = info["factor"]
        suffix = info["suffix"]
        options = info["options"]
        
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
        
        # Save temporary file for audix to use
        temp_path = f"temp_{name}.wav"
        with open(temp_path, "wb") as f:
            f.write(processed_files[name])
        temp_file_paths[name] = temp_path
    
    # Display all versions with advanced audio player and download button side by side
    st.subheader("Generated Versions")
    
    # Display each version with audio player and download button side by side
    for name, data in processed_files.items():
        st.write(f"**{display_names[name]}**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Use audix for advanced audio playback with waveform visualization
            audix(temp_file_paths[name], wavesurfer_options=speed_versions[name]["options"])
        with col2:
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
    
    # Clean up temporary files when the app reruns
    import atexit
    
    def cleanup_temp_files():
        try:
            os.remove(temp_original_path)
            for temp_path in temp_file_paths.values():
                os.remove(temp_path)
        except:
            pass
    
    atexit.register(cleanup_temp_files) 