import streamlit as st
import os
import zipfile
import io
# import pandas as pd # No longer needed
from pydub import AudioSegment
from pydub.effects import normalize

# Note: Page config is set in the main app.py
st.title("💿 Генератор Slowed & Sped Up")

# --- Sidebar Controls (Managed globally by Streamlit for multi-page apps) ---
st.sidebar.header("Настроить версии")

# Define fixed presets with default factors
fixed_presets = {
    "SLOWED": {"default_factor": 0.9, "suffix": "SLOWED"},
    "SUPER_SLOWED": {"default_factor": 0.8, "suffix": "SUPER SLOWED"},
    "ULTRA_SLOWED": {"default_factor": 0.6, "suffix": "ULTRA SLOWED"},
    "SPED_UP": {"default_factor": 1.2, "suffix": "SPED UP"},
    "SUPER_SPED_UP": {"default_factor": 1.4, "suffix": "SUPER SPED UP"} # New preset
}

# Store sidebar selections
# Use session state to keep selections consistent across potential reruns within the page
if 'sidebar_selections' not in st.session_state:
    st.session_state.sidebar_selections = {}

for key, preset in fixed_presets.items():
    # Set default state based on key
    default_enabled = False if key == "SUPER_SPED_UP" else True
    # Check if state exists, otherwise use default
    current_enabled = st.session_state.sidebar_selections.get(key, {}).get('enabled', default_enabled)
    current_factor = st.session_state.sidebar_selections.get(key, {}).get('factor', preset['default_factor'])
    
    enabled = st.sidebar.checkbox(
        f"Включить {preset['suffix']}",
        value=current_enabled, 
        key=f"enable_{key}"
    )
    factor = st.sidebar.slider(
        f"Скорость для {preset['suffix']}",
        min_value=0.1,
        max_value=2.0,
        value=current_factor,
        step=0.05,
        format="%.2f",
        key=f"factor_{key}",
        disabled=not enabled # Disable slider if checkbox is unchecked
    )
    # Update session state
    st.session_state.sidebar_selections[key] = {"enabled": enabled, "factor": factor, "suffix": preset['suffix']}

# --- End Sidebar Controls ---


# Allow uploading various audio formats supported by Pydub/ffmpeg
uploaded_file = st.file_uploader(
    "Выберите аудиофайл (wav, mp3, flac, и т.д.)",
    type=["wav", "mp3", "flac", "ogg", "m4a", "aac"], # Add more formats as needed
    key="uploader_generator" # Unique key for this uploader
)


if uploaded_file is not None:
    # Get the original filename without extension
    original_filename = os.path.splitext(uploaded_file.name)[0]
    original_file_wav_name = f"{original_filename}.wav" # Standardized output name

    # Load the audio directly from the uploaded file bytes using from_file
    audio_bytes = uploaded_file.getvalue()
    audio_io = io.BytesIO(audio_bytes)
    try:
        # Use from_file which detects format based on ffmpeg
        audio = AudioSegment.from_file(audio_io)
    except Exception as e:
        st.error(f"Ошибка загрузки аудиофайла: {e}")
        st.error("Убедитесь, что файл имеет поддерживаемый формат и при необходимости установлен ffmpeg.")
        st.stop()

    # --- Process Files --- 
    processed_files = {} # Store {'key': {'data': bytes, 'suffix': str, 'factor': float or None}}
    
    # Use the selections stored in session state
    sidebar_selections = st.session_state.sidebar_selections

    # Calculate total steps for progress bar (1 for original + number of enabled presets)
    enabled_presets_count = sum(1 for key, sel in sidebar_selections.items() if sel["enabled"]) 
    total_steps = 1 + enabled_presets_count
    progress_bar = st.progress(0, text="Обработка...")
    steps_done = 0

    # 1. Process Original File
    st.write("Обработка оригинала...")
    try:
        original_processed = audio.set_frame_rate(44100).set_sample_width(2)
        original_processed = normalize(original_processed, headroom=0.0) # Normalize to 0dB
        
        output_buffer_orig = io.BytesIO()
        original_processed.export(output_buffer_orig, format="wav")
        processed_files["original"] = {
            "data": output_buffer_orig.getvalue(),
            "suffix": "Оригинал (обработанный)",
            "filename": original_file_wav_name, # Filename for zip and download
            "factor": None # No speed factor for original
        }
        steps_done += 1
        progress_bar.progress(steps_done / total_steps, text=f"Обработка... ({steps_done}/{total_steps})")
    except Exception as e:
        st.error(f"Ошибка обработки оригинала: {e}")
        st.stop()

    # 2. Process Enabled Speed Versions
    st.write("Обработка версий скорости...")
    for key, selection in sidebar_selections.items():
        if selection["enabled"]:
            factor = selection["factor"]
            suffix = selection["suffix"]
            preset_key = f"preset_{key}"
            
            try:
                # Change the speed
                modified_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * factor)
                })

                # Set output format: 44.1 kHz, 16-bit
                modified_audio = modified_audio.set_frame_rate(44100)
                modified_audio = modified_audio.set_sample_width(2)
                
                # Normalize audio to 0dB
                modified_audio = normalize(modified_audio, headroom=0.0)

                # Export the modified audio to bytes as WAV
                output_buffer = io.BytesIO()
                modified_audio.export(output_buffer, format="wav")

                # Store data, suffix, and factor
                processed_files[preset_key] = {
                    "data": output_buffer.getvalue(),
                    "suffix": suffix,
                    "filename": f"{original_filename} ({suffix}).wav",
                    "factor": factor
                }
                steps_done += 1
                progress_bar.progress(steps_done / total_steps, text=f"Обработка... ({steps_done}/{total_steps})")
            except Exception as e:
                 st.error(f"Ошибка обработки версии '{suffix}': {e}")
                 # Continue processing other versions if one fails
                 continue 

    progress_bar.empty()
    st.success("Обработка завершена!")

    # --- Create Zip and Display Results --- 
    if processed_files:
        # Sort files: original first, then by factor
        sorted_keys = sorted(
            processed_files.keys(),
            key=lambda k: (processed_files[k]["factor"] is not None, processed_files[k]["factor"] or 0)
        )
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add all processed files (including original) to the zip
            for key in sorted_keys:
                info = processed_files[key]
                zip_file.writestr(info["filename"], info["data"])

        # Display Download All button
        st.download_button(
            label="Скачать все обработанные версии (.zip)",
            data=zip_buffer.getvalue(),
            file_name=f"{original_filename}_все_версии.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        # Display all versions in an expander
        with st.expander("Посмотреть все обработанные версии", expanded=False):
            # Display original first if it exists
            if "original" in processed_files:
                 info = processed_files["original"]
                 st.subheader(f"{info['suffix']}")
                 st.audio(info['data'], format="audio/wav")
                 st.download_button(
                    label=f"Скачать {info['suffix']}",
                    data=info['data'],
                    file_name=info['filename'],
                    mime="audio/wav",
                    key="download_original_generator"
                 )
                 st.divider()

            # Display speed versions
            for key in sorted_keys:
                 if key != "original": # Skip the original we already displayed
                    info = processed_files[key]
                    st.subheader(f"{info['suffix']} (Скорость: {info['factor']:.2f})")
                    st.audio(info['data'], format="audio/wav")
                    st.download_button(
                        label=f"Скачать версию {info['suffix']}",
                        data=info['data'],
                        file_name=info['filename'],
                        mime="audio/wav",
                        key=f"download_{key}_generator"
                    )
                    st.divider() 
    else:
        st.warning("Не удалось обработать ни одной версии.") 