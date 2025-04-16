import streamlit as st

st.set_page_config(
    page_title="VBR Distrotools",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="expanded" # Keep sidebar open to see pages
)

st.title("🎧 Distrotools")

st.markdown(
    """
    Привет!

    Используй боковое меню для выбора инструмента:

    - **Генератор Slowed & Sped Up:** создает Slowed и Sped Up версии треков.
    - **Аудио Конвертер:** конвертирует треки в стандартный WAV формат (16 бит, 44.1 кГц, нормализация).
    """
) 