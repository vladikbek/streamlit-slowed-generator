import streamlit as st
import os
import zipfile
import io
from pydub import AudioSegment
from pydub.effects import normalize

st.title("🔊 Аудио Конвертер")

st.markdown("Загрузи один или несколько аудиофайлов для конвертации в стандартный WAV формат (16 бит, 44.1 кГц, нормализация до 0 dBFS).")

# Allow uploading multiple audio files
uploaded_files = st.file_uploader(
    "Выберите аудиофайлы (wav, mp3, flac, и т.д.)",
    type=["wav", "mp3", "flac", "ogg", "m4a", "aac"], # Add more formats as needed
    accept_multiple_files=True,
    key="uploader_converter" # Unique key for this uploader
)

# Add a button to trigger processing, disabled if no files are uploaded
start_processing = st.button("Начать обработку", disabled=(not uploaded_files), key="start_converter")

if start_processing and uploaded_files:
    converted_files = {} # Store {'original_filename.wav': data_bytes}
    errors = {} # Store {'original_filename': error_message}
    
    total_files = len(uploaded_files)
    progress_bar = st.progress(0, text="Обработка...")
    
    st.write(f"Обработка {total_files} файла(ов)...")

    for i, uploaded_file in enumerate(uploaded_files):
        original_filename = os.path.splitext(uploaded_file.name)[0]
        target_filename = f"{original_filename}.wav" # Standardized output name
        
        try:
            # st.write(f"  - Processing: {uploaded_file.name}") # Optional: Keep detailed logs or remove
            audio_bytes = uploaded_file.getvalue()
            audio_io = io.BytesIO(audio_bytes)
            
            # Load audio
            audio = AudioSegment.from_file(audio_io)
            
            # Process: Set format and normalize
            converted_audio = audio.set_frame_rate(44100).set_sample_width(2)
            converted_audio = normalize(converted_audio, headroom=0.0)
            
            # Export to buffer
            output_buffer = io.BytesIO()
            converted_audio.export(output_buffer, format="wav")
            converted_files[target_filename] = output_buffer.getvalue()
            
        except Exception as e:
            error_msg = f"Ошибка обработки {uploaded_file.name}: {e}"
            st.error(f"  - {error_msg}")
            errors[uploaded_file.name] = str(e)
        
        # Update progress
        progress_bar.progress((i + 1) / total_files, text=f"Обработка... ({i+1}/{total_files})")

    progress_bar.empty()
    st.success("Обработка завершена!")

    if errors:
        st.warning("Некоторые файлы не удалось обработать:")
        # Display errors more cleanly
        for name, err in errors.items():
            st.text(f"- {name}: {err}")
        
    if converted_files:
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, data in converted_files.items():
                zip_file.writestr(filename, data)
        
        st.download_button(
            label=f"Скачать все конвертированные файлы ({len(converted_files)}) в .zip",
            data=zip_buffer.getvalue(),
            file_name="конвертированные_файлы.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        # Optional: Display previews
        with st.expander("Посмотреть конвертированные файлы"):
            for filename, data in converted_files.items():
                st.subheader(filename)
                st.audio(data, format="audio/wav")
                st.download_button(
                    label=f"Скачать {filename}",
                    data=data,
                    file_name=filename,
                    mime="audio/wav",
                    key=f"download_{filename}_converter"
                )
                st.divider()
    elif not errors: # Only show if no files were converted AND there were no errors (e.g., upload then remove)
        st.info("Файлы не были обработаны.") 