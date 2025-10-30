import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment
from pydub.effects import normalize

# --- Page Config ---
st.set_page_config(
    page_title="Slowed Generator",
    page_icon="⏯️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("💿 Slowed Generator")
st.markdown("Upload a track to create Slowed and Sped Up versions. Speed settings are in the sidebar.")

# --- Sidebar Controls (Managed globally by Streamlit for multi-page apps) ---
with st.sidebar:
    st.header("Configure Versions")

    # Define fixed presets with default values for speed (percentage) and pitch (semitones)
    fixed_presets = {
        "SLOWED": {
            "suffix": "Slowed",
            "defaults": {"speed_factor": 0.9, "speed_percent": 90, "pitch_semitones": -2}
        },
        "SUPER_SLOWED": {
            "suffix": "Super Slowed",
            "defaults": {"speed_factor": 0.8, "speed_percent": 80, "pitch_semitones": -4}
        },
        "ULTRA_SLOWED": {
            "suffix": "Ultra Slowed",
            "defaults": {"speed_factor": 0.6, "speed_percent": 60, "pitch_semitones": -9}
        },
        "MEGA_SLOWED": {
            "suffix": "Mega Slowed",
            "defaults": {"speed_factor": 0.5, "speed_percent": 50, "pitch_semitones": -12}
        },
        "SPED_UP": {
            "suffix": "Sped Up",
            "defaults": {"speed_factor": 1.2, "speed_percent": 120, "pitch_semitones": 3}
        },
        "SUPER_SPED_UP": {
            "suffix": "Super Sped Up",
            "defaults": {"speed_factor": 1.4, "speed_percent": 140, "pitch_semitones": 6}
        }
    }

    mode_label = st.radio(
        "Adjustment mode",
        options=("Speed (%)", "Pitch (semitones)"),
        index=0,
        key="mode_selector"
    )
    mode = "speed" if mode_label.startswith("Speed") else "pitch"

    # Store the current selections from the sidebar for processing
    selections_for_processing = {}

    for key, preset in fixed_presets.items():
        # Set default state for the checkbox (only used on first run for this key)
        default_enabled = False if key in ("MEGA_SLOWED", "SPED_UP", "SUPER_SPED_UP") else True

        # Checkbox state is managed by Streamlit via its key
        enabled = st.checkbox(
            f"Enable {preset['suffix']}",
            value=default_enabled, # Streamlit uses key to restore state on reruns
            key=f"enable_{key}"
        )

        if mode == "speed":
            # Slider state is managed by Streamlit via its key
            factor = st.slider(
                f"Speed for {preset['suffix']}",
                min_value=0.1,
                max_value=2.0,
                value=preset['defaults']['speed_factor'], # Streamlit uses key to restore state on reruns
                step=0.05,
                format="%.2f",
                key=f"factor_{key}",
                disabled=not enabled # Disable based on checkbox's CURRENT value in this run
            )
            label = f"{factor * 100:.0f}%"
        else:
            semitones = st.slider(
                f"Pitch for {preset['suffix']}",
                min_value=-12,
                max_value=12,
                value=preset['defaults']['pitch_semitones'],
                step=1,
                key=f"semitones_{key}",
                disabled=not enabled
            )
            factor = 2 ** (semitones / 12)
            label = f"{semitones:+d} st"

        # Store the current state for later use if processing starts
        selections_for_processing[key] = {
            "enabled": enabled,
            "factor": factor,
            "suffix": preset['suffix'],
            "mode": mode,
            "label": label
        }

# --- End Sidebar Controls ---

# Allow uploading various audio formats supported by Pydub/ffmpeg
uploaded_file = st.file_uploader(
    "Choose a file (wav, mp3, flac, etc.)",
    type=["wav", "mp3", "flac", "ogg", "m4a", "aac"], # Add more formats as needed
    key="uploader_generator" # Unique key for this uploader
)

# Add a button to trigger processing, disabled if no file is uploaded
start_processing = st.button(
    "Start Processing", 
    disabled=(uploaded_file is None), 
    key="start_generator", 
    use_container_width=True
)

# Add checkbox for including original version
include_original = st.checkbox(
    "Include original version in zip archive",
    value=True,  # Default to True (on by default)
    key="include_original"
)

# Placeholder for status messages
status_placeholder_orig = st.empty()
status_placeholder_versions = st.empty()

if start_processing and uploaded_file is not None:
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
        st.error(f"Error loading audio file: {e}")
        st.error("Make sure the file has a supported format and ffmpeg is installed if necessary.")
        st.stop()

    # --- Process Files --- 
    processed_files = {} # Store {'key': {'data': bytes, 'suffix': str, 'factor': float or None, 'mode': str | None, 'label': str | None}}
    
    # Use the selections captured during the sidebar rendering pass
    # No need to read from st.session_state here
    
    # Calculate total steps for progress bar (1 for original if included + number of enabled presets)
    enabled_presets_count = sum(1 for key, sel in selections_for_processing.items() if sel["enabled"]) 
    total_steps = (1 if include_original else 0) + enabled_presets_count
    progress_bar = st.progress(0, text="Processing...")
    steps_done = 0

    # 1. Process Original File (only if include_original is True)
    if include_original:
        status_placeholder_orig.write("Processing original...")
        try:
            original_processed = audio.set_frame_rate(44100).set_sample_width(2)
            original_processed = normalize(original_processed, headroom=0.0) # Normalize to 0dB
            
            output_buffer_orig = io.BytesIO()
            original_processed.export(output_buffer_orig, format="wav")
            processed_files["original"] = {
                "data": output_buffer_orig.getvalue(),
                "suffix": "Original (processed)",
                "filename": original_file_wav_name, # Filename for zip and download
                "factor": None, # No speed factor for original
                "mode": None,
                "label": None
            }
            steps_done += 1
            progress_bar.progress(steps_done / total_steps, text=f"Processing... ({steps_done}/{total_steps})")
        except Exception as e:
            st.error(f"Error processing original: {e}")
            st.stop()
        status_placeholder_orig.empty() # Clear original processing message

    # 2. Process Enabled Speed Versions
    if enabled_presets_count > 0:
        status_placeholder_versions.write("Processing versions...")
        # Use the selections captured earlier
        for key, selection in selections_for_processing.items():
            if selection["enabled"]:
                factor = selection["factor"]
                suffix = selection["suffix"]
                label = selection["label"]
                selection_mode = selection["mode"]
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
                        "factor": factor,
                        "mode": selection_mode,
                        "label": label
                    }
                    steps_done += 1
                    progress_bar.progress(steps_done / total_steps, text=f"Processing... ({steps_done}/{total_steps})")
                except Exception as e:
                    st.error(f"Error processing version '{suffix}': {e}")
                    # Continue processing other versions if one fails
                    continue 
        status_placeholder_versions.empty() # Clear versions processing message

    progress_bar.empty()
    st.success("Processing completed!")

    # --- Create Zip and Display Results --- 
    if processed_files:
        # Sort files: original first, then by factor
        sorted_keys = sorted(
            processed_files.keys(),
            key=lambda k: (processed_files[k]["factor"] is not None, processed_files[k]["factor"] or 0)
        )
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add all processed files (including original if enabled) to the zip
            for key in sorted_keys:
                info = processed_files[key]
                zip_file.writestr(info["filename"], info["data"])

        # Display Download All button
        st.download_button(
            label="Download all processed versions (.zip)",
            data=zip_buffer.getvalue(),
            file_name=f"{original_filename}_all_versions.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        # Display all versions in an expander
        with st.expander("View all processed versions", expanded=False):
            # Display original first if it exists
            if "original" in processed_files:
                info = processed_files["original"]
                st.subheader(f"{info['suffix']}")
                st.audio(info['data'], format="audio/wav")
                st.download_button(
                    label=f"Download {info['suffix']}",
                    data=info['data'],
                    file_name=info['filename'],
                    mime="audio/wav",
                    key="download_original_generator"
                )
                st.divider()

            # Display processed versions
            for key in sorted_keys:
                if key != "original": # Skip the original we already displayed
                    info = processed_files[key]
                    descriptor = None
                    if info.get("mode") == "pitch" and info.get("label"):
                        descriptor = f"Pitch: {info['label']}"
                    elif info.get("mode") == "speed" and info.get("label"):
                        descriptor = f"Speed: {info['label']}"

                    title = info['suffix'] if not descriptor else f"{info['suffix']} ({descriptor})"
                    st.subheader(title)
                    st.audio(info['data'], format="audio/wav")
                    st.download_button(
                        label=f"Download {info['suffix']} version",
                        data=info['data'],
                        file_name=info['filename'],
                        mime="audio/wav",
                        key=f"download_{key}_generator"
                    )
                    st.divider()
    else:
        st.warning("Failed to process any versions.") 
