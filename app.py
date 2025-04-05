import streamlit as st
import os
import zipfile
import io
import pandas as pd  # Import pandas for data editor
from pydub import AudioSegment
from pydub.effects import normalize

st.set_page_config(
    page_title="Slowed & Sped Up Generator",
    page_icon="💿",
    layout="centered"
)

st.title("💿 Slowed & Sped Up Generator")

# Allow uploading various audio formats supported by Pydub/ffmpeg
uploaded_file = st.file_uploader(
    "Choose an audio file (wav, mp3, flac, etc.)",
    type=["wav", "mp3", "flac", "ogg", "m4a", "aac"] # Add more formats as needed
)

# --- Preset Editor ---
st.subheader("Speed Presets")
# Default presets data
default_presets_data = {
    "Suffix": ["SLOWED", "SUPER SLOWED", "ULTRA SLOWED", "SPED UP"],
    "Factor": [0.9, 0.8, 0.6, 1.2]
}
default_presets_df = pd.DataFrame(default_presets_data)

# Use data editor for customizable presets
edited_presets_df = st.data_editor(
    default_presets_df,
    num_rows="dynamic", # Allow adding/deleting rows
    use_container_width=True,
    column_config={
        "Factor": st.column_config.NumberColumn(
            "Speed Factor",
            help="Speed multiplier (e.g., 0.8 for 80% speed, 1.2 for 120%)",
            min_value=0.1,
            max_value=5.0,
            step=0.05,
            format="%.2f",
            required=True,
        ),
         "Suffix": st.column_config.TextColumn(
            "Suffix",
            help="Text added to the filename (e.g., SLOWED)",
            required=True,
        )
    }
)
# --- End Preset Editor ---


if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]

    # Load the audio directly from the uploaded file bytes using from_file
    audio_bytes = uploaded_file.getvalue()
    audio_io = io.BytesIO(audio_bytes)
    try:
        # Use from_file which detects format based on ffmpeg
        audio = AudioSegment.from_file(audio_io)
    except Exception as e:
        st.error(f"Error loading audio file: {e}")
        st.error("Please ensure the file is a valid audio format and ffmpeg is installed if needed.")
        st.stop()

    # Use the presets from the data editor
    # Validate the edited presets DataFrame
    if edited_presets_df['Factor'].isnull().any() or edited_presets_df['Suffix'].isnull().any() or (edited_presets_df['Suffix'] == '').any():
        st.warning("Please ensure all presets have a valid Factor and Suffix.")
    else:
        processed_files_with_suffix = {} # Store {'preset_key': {'data': bytes, 'suffix': 'SLOWED'}}

        progress_bar = st.progress(0)
        total_presets = len(edited_presets_df)

        for index, row in edited_presets_df.iterrows():
            factor = row['Factor']
            suffix = row['Suffix']
            preset_key = f"preset_{index}" # Unique key for this preset

            # --- Audio Processing ---
            # Change the speed using frame rate manipulation
            # Pydub handles both slowing down and speeding up correctly this way
            modified_audio = audio._spawn(audio.raw_data, overrides={
                 "frame_rate": int(audio.frame_rate * factor)
            })
            # No need to set frame rate back here, export handles final format

            # Normalize audio
            modified_audio = normalize(modified_audio, headroom=0.1)

            # Set output format: 44.1 kHz, 16-bit
            modified_audio = modified_audio.set_frame_rate(44100)
            modified_audio = modified_audio.set_sample_width(2) # 2 bytes = 16 bit
            # --- End Audio Processing ---

            # Export the modified audio to bytes as WAV
            output_buffer = io.BytesIO()
            modified_audio.export(output_buffer, format="wav")

            # Store data and suffix
            processed_files_with_suffix[preset_key] = {
                "data": output_buffer.getvalue(),
                "suffix": suffix
            }

            # Update progress bar
            progress_bar.progress((index + 1) / total_presets)


        # Create a zip file with all versions
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add all modified versions with their display names
            for key, info in processed_files_with_suffix.items():
                file_name = f"{original_filename} ({info['suffix']}).wav"
                zip_file.writestr(file_name, info['data'])

        # Display Download All button
        st.download_button(
            label="Download All Versions (.zip)",
            data=zip_buffer.getvalue(),
            file_name=f"{original_filename}_all_versions.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        # Display all versions in an expander
        with st.expander("View All Versions"):
            for key, info in processed_files_with_suffix.items():
                st.subheader(f"{info['suffix']} (Factor: {edited_presets_df.loc[int(key.split('_')[1]), 'Factor']:.2f})")
                st.audio(info['data'], format="audio/wav")
                # Optional: Add individual download buttons
                st.download_button(
                    label=f"Download {info['suffix']} Version",
                    data=info['data'],
                    file_name=f"{original_filename} ({info['suffix']}).wav",
                    mime="audio/wav",
                    key=f"download_{key}" # Unique key for download button
                )
                st.divider() # Add a divider between versions 