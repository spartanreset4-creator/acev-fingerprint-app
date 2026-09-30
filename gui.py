import datetime
import cv2
import numpy as np
import streamlit as st

from src.analysis.minutiae import MinutiaeExtractor
from src.analysis.preprocessing import FingerprintPreprocessor
from src.analysis.pattern import PatternClassifier
from src.comparison.matcher import MinutiaeMatcher
from src.evaluation.decision import Evaluator
from src.utils.visualization import draw_minutiae
from src.utils.pdf_generator import generate_pdf_report
from src.verification.audit import VerificationAudit

st.set_page_config(
    page_title="Sistema Forense ACE-V - Identificación Dactilar",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Sistema Forense de Identificación Dactilar (ACE-V)")
st.markdown(
    "Plataforma interactiva para el procesamiento, clasificación, comparación, evaluación y verificación forense según el protocolo **ACE-V**."
)

# Panel lateral: Parámetros y Carga de Imágenes
st.sidebar.header("⚙️ Configuración del Análisis")
block_size = st.sidebar.slider("Tamaño de Bloque (Gabor)", 8, 32, 16, step=4)
border_margin = st.sidebar.slider("Margen de Borde (Minucias)", 5, 20, 10)
dist_threshold = st.sidebar.slider("Umbral de Distancia (px)", 5.0, 25.0, 12.0)

st.sidebar.markdown("---")
st.sidebar.header("📁 Carga de Huellas")
file_a = st.sidebar.file_uploader("1. Huella Dudosa / Latente (A)", type=["png", "jpg", "jpeg", "bmp", "tif"])
file_b = st.sidebar.file_uploader("2. Huella de Referencia / Decadactilar (B)", type=["png", "jpg", "jpeg", "bmp", "tif"])


def process_fingerprint(image_bytes, block_size, border_margin):
    """Procesa una huella individual: Preprocesamiento, Extracción y Clasificación."""
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    preprocessor = FingerprintPreprocessor(block_size=block_size)
    normalized = preprocessor.normalize(image)
    orientation = preprocessor.estimate_orientation_map(normalized)
    enhanced = preprocessor.apply_gabor_filter(normalized, orientation)
    skeleton = preprocessor.binarize_and_thin(enhanced)

    extractor = MinutiaeExtractor(border_margin=border_margin)
    minutiae = extractor.extract(skeleton)
    minutiae_img = draw_minutiae(skeleton, minutiae["terminations"], minutiae["bifurcations"])

    classifier = PatternClassifier(block_size=block_size)
    pattern_info = classifier.classify(orientation)

    return {
        "raw": image,
        "orientation": orientation,
        "enhanced": enhanced,
        "skeleton": skeleton,
        "minutiae": minutiae,
        "minutiae_img": minutiae_img,
        "pattern_info": pattern_info,
    }


def generate_report(data_a, data_b, match_result, evaluation, audit_result=None, pattern_a="Indeterminado", pattern_b="Indeterminado") -> str:
    """Genera informe en texto plano."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = []
    report.append("=========================================================")
    report.append("       INFORME DE COTEJO DACTILOSCÓPICO FORENSE          ")
    report.append("                  METODOLOGÍA ACE-V                      ")
    report.append("=========================================================")
    report.append(f"Fecha de emisión: {now_str}")
    report.append("")

    report.append("1. FASE A - ANÁLISIS (ANALYSIS)")
    report.append(f" - Huella A (Dudosa): Patrón [{pattern_a}] | {len(data_a['minutiae']['terminations'])} terminaciones, {len(data_a['minutiae']['bifurcations'])} bifurcaciones.")
    report.append(f" - Huella B (Referencia): Patrón [{pattern_b}] | {len(data_b['minutiae']['terminations'])} terminaciones, {len(data_b['minutiae']['bifurcations'])} bifurcaciones.")
    report.append("")

    report.append("2. FASE C - COMPARACIÓN (COMPARISON)")
    report.append(f" - Umbral espacial utilizado: {match_result.get('threshold', 12)} px")
    report.append(f" - Minucias coincidentes: {match_result['matches']}")
    report.append(f" - Índice de similitud: {match_result['score'] * 100:.2f}%")
    report.append("")

    report.append("3. FASE E - EVALUACIÓN (EVALUATION)")
    report.append(f" - Dictamen: {evaluation['decision']}")
    report.append(f" - Confianza: {evaluation['confidence']}")
    report.append(f" - Fundamentación: {evaluation['reason']}")
    report.append("")

    report.append("4. FASE V - VERIFICACIÓN (VERIFICATION)")
    if audit_result:
        report.append(f" - Perito Verificador: {audit_result['verifier']}")
        report.append(f" - Estado Auditoría: {audit_result['verification_status']}")
        report.append(f" - Fecha/Hora Auditoría: {audit_result['verification_time']}")
        report.append(f" - Observaciones: {audit_result['verifier_notes'] if audit_result['verifier_notes'] else 'N/A'}")
    else:
        report.append(" - Estado: Pendiente de Verificación por un segundo perito.")

    report.append("=========================================================")
    return "\n".join(report)


if file_a is not None and file_b is not None:
    # ---------------------------------------------------------
    # FASE 1: ANÁLISIS (A)
    # ---------------------------------------------------------
    st.header("1. Fase de Análisis (Analysis)")

    with st.spinner("Procesando, clasificando y extrayendo minucias de ambas impresiones..."):
        data_a = process_fingerprint(file_a.read(), block_size, border_margin)
        data_b = process_fingerprint(file_b.read(), block_size, border_margin)

    pattern_options = [
        "Arco (Adeltico)",
        "Presilla Interna / Radial (Monodeltico)",
        "Presilla Externa / Cubital (Monodeltico)",
        "Verticilo (Bideltico)",
        "Inconcluso / Dañado"
    ]

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Huella A (Dudosa / Latente)")
        st.image(cv2.cvtColor(data_a["minutiae_img"], cv2.COLOR_BGR2RGB), width="stretch")
        st.caption(
            f"Terminaciones: {len(data_a['minutiae']['terminations'])} | "
            f"Bifurcaciones: {len(data_a['minutiae']['bifurcations'])}"
        )
        st.info(f"🤖 **Detección Algorítmica:** {data_a['pattern_info']['predicted_pattern']} ({data_a['pattern_info']['deltas_count']} Deltas / {data_a['pattern_info']['cores_count']} Núcleos)")
        
        idx_a = 0 if "Arco" in data_a['pattern_info']['predicted_pattern'] else (1 if "Presilla" in data_a['pattern_info']['predicted_pattern'] else 3)
        final_pattern_a = st.selectbox("Confirmación Pericial (Huella A):", options=pattern_options, index=idx_a, key="pat_a")

    with col_b:
        st.subheader("Huella B (Referencia)")
        st.image(cv2.cvtColor(data_b["minutiae_img"], cv2.COLOR_BGR2RGB), width="stretch")
        st.caption(
            f"Terminaciones: {len(data_b['minutiae']['terminations'])} | "
            f"Bifurcaciones: {len(data_b['minutiae']['bifurcations'])}"
        )
        st.info(f"🤖 **Detección Algorítmica:** {data_b['pattern_info']['predicted_pattern']} ({data_b['pattern_info']['deltas_count']} Deltas / {data_b['pattern_info']['cores_count']} Núcleos)")
        
        idx_b = 0 if "Arco" in data_b['pattern_info']['predicted_pattern'] else (1 if "Presilla" in data_b['pattern_info']['predicted_pattern'] else 3)
        final_pattern_b = st.selectbox("Confirmación Pericial (Huella B):", options=pattern_options, index=idx_b, key="pat_b")

    st.markdown("---")

    # ---------------------------------------------------------
    # FASE 2: COMPARACIÓN (C)
    # ---------------------------------------------------------
    st.header("2. Fase de Comparación (Comparison)")

    matcher = MinutiaeMatcher(distance_threshold=dist_threshold)
    match_result = matcher.align_and_match(data_a["minutiae"], data_b["minutiae"])
    match_result["threshold"] = dist_threshold

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Minucias Coincidentes", match_result["matches"])
    m_col2.metric("Score de Similitud", f"{match_result['score'] * 100:.1f}%")
    m_col3.metric("Umbral Distancia Utilizado", f"{dist_threshold} px")

    st.markdown("---")

    # ---------------------------------------------------------
    # FASE 3: EVALUACIÓN (E)
    # ---------------------------------------------------------
    st.header("3. Fase de Evaluación (Evaluation)")

    evaluator = Evaluator()
    evaluation = evaluator.evaluate(match_result)

    decision_text = evaluation["decision"]
    reason_text = evaluation["reason"]

    if "IDENTIFICACIÓN" in decision_text:
        st.success(f"### Dictamen Primario: {decision_text}")
    elif "EXCLUSIÓN" in decision_text:
        st.error(f"### Dictamen Primario: {decision_text}")
    else:
        st.warning(f"### Dictamen Primario: {decision_text}")

    st.write(f"**Fundamentación Técnica:** {reason_text}")
    st.write(f"**Nivel de Confianza:** {evaluation['confidence']}")

    with st.expander("Ver detalle de pares de minucias emparejados"):
        st.json(match_result["matched_pairs"][:15])

    st.markdown("---")

    # ---------------------------------------------------------
    # FASE 4: VERIFICACIÓN (V)
    # ---------------------------------------------------------
    st.header("4. Fase de Verificación (Verification)")
    st.markdown("Auditoría independiente realizada por un segundo perito dactiloscópico.")

    v_col1, v_col2 = st.columns(2)

    with v_col1:
        verifier_name = st.text_input("Nombre del Perito Verificador", value="Lcdo. Ángel Coello")
        verifier_id = st.text_input("Código / Credencial Pericial", value="PER-FORENSE-2026")

    with v_col2:
        agreement = st.radio("Conclusión de la Auditoría", ["Conforme con el Dictamen", "En Disconformidad / Requiere Revisión"])
        verifier_notes = st.text_area("Observaciones del Verificador", value="Revisión ciega realizada conforme a los estándares institucionales. Puntos coincidentes validados.")

    is_agree = agreement == "Conforme con el Dictamen"
    audit = VerificationAudit(verifier_name=verifier_name, verifier_id=verifier_id)
    audit_result = audit.verify_decision(evaluation, agree=is_agree, notes=verifier_notes)

    if is_agree:
        st.info(f"✅ Auditoría confirmada por **{audit_result['verifier']}** a las {audit_result['verification_time']}.")
    else:
        st.warning(f"⚠️ Auditoría registrada con disconformidad por **{audit_result['verifier']}**.")

    st.markdown("---")

    # ---------------------------------------------------------
    # GENERACIÓN Y DESCARGA DEL REPORTE
    # ---------------------------------------------------------
    st.header("📄 Reporte Pericial Final")

    report_content = generate_report(data_a, data_b, match_result, evaluation, audit_result, final_pattern_a, final_pattern_b)
    pdf_buffer = generate_pdf_report(data_a, data_b, match_result, evaluation, audit_result, final_pattern_a, final_pattern_b)

    with st.expander("Vista Previa del Informe Dactiloscópico (Texto)"):
        st.code(report_content, language="text")

    col_down1, col_down2 = st.columns(2)

    with col_down1:
        st.download_button(
            label="📥 Descargar Informe Pericial (.txt)",
            data=report_content,
            file_name=f"Informe_ACE-V_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col_down2:
        st.download_button(
            label="📄 Descargar Informe Pericial Oficial (.pdf)",
            data=pdf_buffer,
            file_name=f"Informe_Oficial_ACE-V_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

else:
    st.info("👈 Sube **ambas imágenes** (Huella Dudosa y Huella de Referencia) desde el panel lateral para ejecutar el proceso ACE-V completo.")