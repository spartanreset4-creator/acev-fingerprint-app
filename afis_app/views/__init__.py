import streamlit as st
import cv2
import numpy as np

# Importamos las funciones puras desde nuestro módulo core
from core.preprocessing import load_image_from_bytes, process_fingerprint_pipeline
from core.minutiae import extract_minutiae, draw_minutiae

def render_afis_page():
    st.header("🔬 Módulo de Análisis y Extracción Dactiloscópica")
    st.markdown("---")

    # Cargar archivo de huella
    uploaded_file = st.file_uploader(
        "Cargar imagen de huella dactilar", 
        type=["png", "jpg", "jpeg", "bmp", "tif"]
    )

    if uploaded_file is not None:
        # 1. Leer bytes de la imagen subida
        file_bytes = uploaded_file.read()
        image_bgr = load_image_from_bytes(file_bytes)

        if image_bgr is None:
            st.error("Error al cargar la imagen. Intenta con otro archivo.")
            return

        # 2. Ejecutar Pipeline de Procesamiento Digital
        gray, binary, skeleton = process_fingerprint_pipeline(image_bgr)

        # 3. Extracción de Minucias (CN)
        terminations, bifurcations = extract_minutiae(skeleton)
        result_img = draw_minutiae(gray, terminations, bifurcations)

        # 4. Organización visual en pestañas (Tabs)
        tab1, tab2, tab3 = st.tabs(["🖼️ Imagen Original", "⚡ Procesamiento Digital", "📍 Minucias Detección"])

        with tab1:
            st.subheader("Vista Previa")
            st.image(gray, caption="Huella en Escala de Grises", use_container_width=True)

        with tab2:
            st.subheader("Etapas del Algoritmo")
            col1, col2 = st.columns(2)
            col1.image(binary, caption="Binarización (Otsu)", use_container_width=True)
            col2.image(skeleton, caption="Esqueletización (Thinning)", use_container_width=True)

        with tab3:
            st.subheader("Puntos Característicos Detectados (CN)")
            st.image(result_img, caption="Rojo: Terminaciones | Azul: Bifurcaciones", use_container_width=True)

            # Métricas e indicadores
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Terminaciones", len(terminations))
            m_col2.metric("Bifurcaciones", len(bifurcations))
            m_col3.metric("Total Minucias", len(terminations) + len(bifurcations))