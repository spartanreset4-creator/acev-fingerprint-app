import streamlit as st
import cv2
import numpy as np
import plotly.express as px
from esqueleto_engine import extraer_esqueleto_y_minucias

st.set_page_config(page_title="AFIS SPECTRA-GUARD", layout="wide")
st.title("🔬 Procesamiento e Identificación Dactiloscópica")

def mostrar_imagen_interactiva(img, titulo):
    """
    Renderiza cualquier matriz de imagen con Plotly garantizando alta fidelidad de líneas delgadas.
    """
    if len(img.shape) == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    fig = px.imshow(img_rgb)
    fig.update_layout(
        title=titulo,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        height=600
    )
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    
    st.plotly_chart(fig, use_container_width=True)


archivo_subido = st.file_uploader("Cargar fotografía de huella dactilar", type=["jpg", "png", "jpeg"])

if archivo_subido is not None:
    # 1. Cargar imagen original
    file_bytes = np.asarray(bytearray(archivo_subido.read()), dtype=np.uint8)
    img_orig = cv2.imdecode(file_bytes, 1)

    # 2. Desempaquetado seguro (soporta retorno de 3 o 4 elementos)
    resultado = extraer_esqueleto_y_minucias(img_orig)
    
    if len(resultado) == 4:
        img_bin, img_esq, img_min, lista_minucias = resultado
    else:
        img_bin, img_min, lista_minucias = resultado
        # Generar esqueleto puro a partir de la imagen de minucias para compatibilidad
        gray_min = cv2.cvtColor(img_min, cv2.COLOR_BGR2GRAY)
        _, img_esq = cv2.threshold(gray_min, 1, 255, cv2.THRESH_BINARY)

    st.info("💡 **Tips:** Usa el scroll del mouse o la herramienta de recuadro en la esquina superior para hacer Zoom preciso sobre cualquier sección de la huella.")

    # 3. Mostrar en las 4 pestañas requeridas
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Foto Original", 
        "2. Binarizada (Contraste)", 
        "3. Esqueleto Puro", 
        "4. Mapa de Minucias"
    ])

    with tab1:
        mostrar_imagen_interactiva(img_orig, "Fotografía Original")

    with tab2:
        mostrar_imagen_interactiva(img_bin, "Máscara Binarizada (Crestas Anchas)")

    with tab3:
        mostrar_imagen_interactiva(img_esq, "Esqueleto Dactilar (1 Píxel de grosor)")

    with tab4:
        col_img, col_info = st.columns([3, 1])
        with col_img:
            mostrar_imagen_interactiva(img_min, "Minucias y Características Dactilares")
        with col_info:
            st.subheader("Conteo Forense")
            fines = sum(1 for m in lista_minucias if m['tipo'] == 'Fin de Cresta')
            bifurcaciones = sum(1 for m in lista_minucias if m['tipo'] == 'Bifurcación')
            
            st.metric("Fines de Cresta (Rojo)", fines)
            st.metric("Bifurcaciones (Azul)", bifurcaciones)
            st.metric("Total Minucias", len(lista_minucias))