import streamlit as st
from views.afis_analyzer import render_afis_page

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema AFIS - Dactiloscopia",
    page_icon="🔬",
    layout="wide"
)

# Sidebar - Menú Navegación
st.sidebar.title("Navegación AFIS")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Selecciona un Módulo:",
    ["🏠 Inicio / Dashboard", "🔬 Analizador de Huellas", "🔍 Buscador & Cotejo", "⚙️ Configuración"]
)

# Control de navegación
if opcion == "🏠 Inicio / Dashboard":
    st.title("🛡️ Sistema de Identificación Dactiloscópica (AFIS)")
    st.write("Bienvenido a la plataforma central de procesamiento y análisis forense de huellas dactilares.")
    st.info("Selecciona **'🔬 Analizador de Huellas'** en el menú lateral para procesar una muestra.")

elif opcion == "🔬 Analizador de Huellas":
    render_afis_page()

elif opcion == "🔍 Buscador & Cotejo":
    st.title("🔍 Módulo de Cotejo 1:N")
    st.info("Este módulo para comparar contra la base de datos se integrará en la siguiente fase.")

elif opcion == "⚙️ Configuración":
    st.title("⚙️ Ajustes del Sistema")
    st.write("Ajustes de umbrales y parámetros de procesamiento.")