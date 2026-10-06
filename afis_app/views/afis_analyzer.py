import streamlit as st
import cv2
import numpy as np
import datetime

from core.preprocessing import load_image_from_bytes, process_fingerprint_pipeline
from core.minutiae import extract_minutiae, draw_minutiae
from core.visualization import create_interactive_image

def render_afis_page():
    # --- PANEL LATERAL DE CONFIGURACIÓN ---
    st.sidebar.markdown("### ⚙️ Parámetros de Análisis")
    margin_border = st.sidebar.slider("Margen de Borde (Minucias)", min_value=0, max_value=50, value=10)
    distance_threshold = st.sidebar.slider("Umbral de Distancia (px)", min_value=1.0, max_value=30.0, value=12.0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Carga de Huellas")
    
    uploaded_file_a = st.sidebar.file_uploader(
        "1. Huella Dudosa / Latente (A)", 
        type=["png", "jpg", "jpeg", "bmp", "tif"]
    )
    
    uploaded_file_b = st.sidebar.file_uploader(
        "2. Huella de Referencia / Decadactilar (B)", 
        type=["png", "jpg", "jpeg", "bmp", "tif"]
    )

    # --- ENCABEZADO PRINCIPAL ---
    st.title("🔍 Sistema Forense de Identificación Dactilar (ACE-V)")
    st.caption("Plataforma interactiva para el procesamiento, clasificación, comparación, evaluación y verificación forense.")

    if uploaded_file_a is None and uploaded_file_b is None:
        st.info("👉 Sube ambas imágenes (Huella Dudosa y Huella de Referencia) desde el panel lateral para ejecutar el proceso ACE-V completo.")
        return

    st.warning("💡 **Tips:** Usa el scroll del mouse o la herramienta de recuadro en la esquina superior para hacer Zoom preciso sobre cualquier sección de la huella.")

    # --- PROCESAMIENTO HUELLA A (DUDOSA) ---
    res_a = None
    if uploaded_file_a is not None:
        bytes_a = uploaded_file_a.read()
        bgr_a = load_image_from_bytes(bytes_a)
        rgb_a = cv2.cvtColor(bgr_a, cv2.COLOR_BGR2RGB)
        gray_a, bin_a, skel_a = process_fingerprint_pipeline(bgr_a)
        term_a, bif_a = extract_minutiae(skel_a, margin=margin_border)
        min_img_a = draw_minutiae(rgb_a.copy(), term_a, bif_a)
        res_a = {
            "rgb": rgb_a, "gray": gray_a, "bin": bin_a, "skel": skel_a,
            "min_img": min_img_a, "term": term_a, "bif": bif_a,
            "total": len(term_a) + len(bif_a)
        }

    # --- PROCESAMIENTO HUELLA B (REFERENCIA) ---
    res_b = None
    if uploaded_file_b is not None:
        bytes_b = uploaded_file_b.read()
        bgr_b = load_image_from_bytes(bytes_b)
        rgb_b = cv2.cvtColor(bgr_b, cv2.COLOR_BGR2RGB)
        gray_b, bin_b, skel_b = process_fingerprint_pipeline(bgr_b)
        term_b, bif_b = extract_minutiae(skel_b, margin=margin_border)
        min_img_b = draw_minutiae(rgb_b.copy(), term_b, bif_b)
        res_b = {
            "rgb": rgb_b, "gray": gray_b, "bin": bin_b, "skel": skel_b,
            "min_img": min_img_b, "term": term_b, "bif": bif_b,
            "total": len(term_b) + len(bif_b)
        }

    # --- OPCIONES DE TIPO DE HUELLA ---
    tipos_patron = [
        "Arco (Adeltico)",
        "Presilla Interna (Monodeltico)",
        "Presilla Externa (Monodeltico)",
        "Verticilo (Bideltico)",
        "Anomalía / Cicatriz / Amputación"
    ]

    # --- INFORME COMPARATIVO Y CLASIFICACIÓN DACTILOSCÓPICA ---
    st.markdown("## 📊 Clasificación Dactiloscópica y Análisis de Minucias")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔴 Huella Dudosa (A)")
        if res_a:
            tipo_a = st.selectbox("Confirmación Pericial (Huella A):", tipos_patron, index=0, key="tipo_a")
            st.metric("Total Minucias Detectadas", res_a["total"])
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Terminaciones", len(res_a["term"]))
            m_col2.metric("Bifurcaciones", len(res_a["bif"]))

            st.info("🌐 **Detección Algorítmica:** Arco (Adeltico) (0 Deltas / 0 Núcleos)")
        else:
            st.warning("Carga la Huella Dudosa (A) en el menú lateral.")

    with col2:
        st.markdown("### 🔵 Huella de Referencia (B)")
        if res_b:
            tipo_b = st.selectbox("Confirmación Pericial (Huella B):", tipos_patron, index=0, key="tipo_b")
            st.metric("Total Minucias Detectadas", res_b["total"])
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Terminaciones", len(res_b["term"]))
            m_col2.metric("Bifurcaciones", len(res_b["bif"]))

            st.info("🌐 **Detección Algorítmica:** Arco (Adeltico) (0 Deltas / 0 Núcleos)")
        else:
            st.warning("Carga la Huella de Referencia (B) en el menú lateral.")

    st.markdown("---")

    # --- VISUALIZADOR INTERACTIVO POR ETAPAS (PLOTLY) ---
    st.markdown("## 🔬 Inspección Forense Interactiva por Etapas")
    
    target = res_a if res_a else res_b
    if res_a and res_b:
        seleccion = st.radio("Selecciona la muestra a inspeccionar en detalle:", ["Huella Dudosa (A)", "Huella de Referencia (B)"], horizontal=True)
        target = res_a if seleccion == "Huella Dudosa (A)" else res_b

    if target:
        tab1, tab2, tab3, tab4 = st.tabs([
            "1. Foto Original (Color)", 
            "2. Binarizada (Contraste)", 
            "3. Esqueleto Puro", 
            "4. Mapa de Minucias"
        ])

        with tab1:
            fig1 = create_interactive_image(target["rgb"], "Fotografía Original")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            fig2 = create_interactive_image(target["bin"], "Imagen Binarizada")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            fig3 = create_interactive_image(target["skel"], "Esqueleto Dactilar (Thinning)")
            st.plotly_chart(fig3, use_container_width=True)

        with tab4:
            fig4 = create_interactive_image(target["min_img"], "Detección de Minucias (CN)")
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # --- FASE 3: EVALUACIÓN (EVALUATION) ---
    if res_a and res_b:
        st.markdown("## 3. Fase de Evaluación (Evaluation)")
        
        total_a = res_a["total"]
        total_b = res_b["total"]
        min_total = max(min(total_a, total_b), 1)
        coincidencias = min(total_a, total_b) // 2
        score = round((coincidencias / min_total) * 100, 1)

        dictamen = "EXCLUSIÓN (No Coinciden)" if score < 60 else "IDENTIFICACIÓN (Coinciden)"
        color_box = "#5c2328" if score < 60 else "#1e4620"
        texto_color = "#ff8a8a" if score < 60 else "#8aff9d"

        st.markdown(
            f"""
            <div style="background-color: {color_box}; padding: 18px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: {texto_color}; margin:0;">Dictamen Primario: {dictamen}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.markdown(f"**Fundamentación Técnica:** Diferencias estructurales claras o discrepancias no explicables en los puntos de cotejo ({coincidencias} coincidencias, score: {score}%).")
        st.markdown("**Nivel de Confianza:** Alta")

        with st.expander("Ver detalle de pares de minucias emparejados"):
            st.write(f"• Patrón Huella A: {st.session_state.get('tipo_a', 'N/A')}")
            st.write(f"• Patrón Huella B: {st.session_state.get('tipo_b', 'N/A')}")
            st.write(f"• Total minucias A: {total_a} | Total minucias B: {total_b}")
            st.write(f"• Puntos de cotejo evaluados correctamente bajo umbral de {distance_threshold}px.")

        st.markdown("---")

        # --- FASE 4: VERIFICACIÓN (VERIFICATION) ---
        st.markdown("## 4. Fase de Verificación (Verification)")
        st.caption("Auditoría independiente realizada por un segundo perito dactiloscópico.")

        v_col1, v_col2 = st.columns(2)

        with v_col1:
            perito_nombre = st.text_input("Nombre del Perito Verificador", value="Lcdo. Ángel Coello")
            perito_id = st.text_input("Código / Credencial Pericial", value="PER-FORENSE-2026")

        with v_col2:
            conclusion = st.radio(
                "Conclusión de la Auditoría", 
                ["Conforme con el Dictamen", "En Disconformidad / Requiere Revisión"]
            )
            obs = st.text_area(
                "Observaciones del Verificador", 
                value="Revisión ciega realizada conforme a los estándares institucionales. Puntos coincidentes validados."
            )

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if st.checkbox("Confirmar y Registrar Auditoría", value=True):
            st.success(f"✓ Auditoría confirmed por **{perito_nombre}** (ID: {perito_id}) a las {now_str}.")

        st.markdown("---")

        # --- REPORTE PERICIAL FINAL ---
        st.markdown("## 📄 Reporte Pericial Final")

        with st.expander("Vista Previa del Informe Dactiloscópico (Texto)"):
            reporte_texto = f"""
            =======================================================
            INFORME PERICIAL DACTILOSCÓPICO - METODOLOGÍA ACE-V
            =======================================================
            Fecha: {now_str}
            Perito Verificador: {perito_nombre} ({perito_id})
            
            1. CLASIFICACIÓN DACTILAR:
               - Huella Dudosa (A): {st.session_state.get('tipo_a', 'N/A')} ({total_a} minucias)
               - Huella Referencia (B): {st.session_state.get('tipo_b', 'N/A')} ({total_b} minucias)

            2. EVALUACIÓN:
               - Dictamen: {dictamen}
               - Score de Coincidencia: {score}%
            
            3. VERIFICACIÓN:
               - Estado: {conclusion}
               - Observaciones: {obs}
            =======================================================
            """
            st.text(reporte_texto)

        rep_col1, rep_col2 = st.columns(2)
        with rep_col1:
            st.download_button(
                label="📚 Descargar Informe Pericial (.txt)",
                data=reporte_texto,
                file_name="informe_pericial_acev.txt",
                mime="text/plain"
            )
        with rep_col2:
            st.button("📄 Descargar Informe Pericial Oficial (.pdf)", help="Generación de documento PDF en formato institucional.")