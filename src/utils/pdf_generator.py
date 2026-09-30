from io import BytesIO
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_pdf_report(
    data_a, data_b, match_result, evaluation, audit_result, pattern_a: str = "Indeterminado", pattern_b: str = "Indeterminado"
) -> BytesIO:
    """Genera un informe pericial dactiloscópico profesional en formato PDF en memoria."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Centrado
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2D3748'),
    )

    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold',
    )

    story = []

    # Encabezado del documento
    story.append(Paragraph("INFORME DE COTEJO DACTILOSCÓPICO FORENSE", title_style))
    story.append(Paragraph("METODOLOGÍA ACE-V (ANALYSIS, COMPARISON, EVALUATION, VERIFICATION)", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1A365D'), spaceAfter=12))

    # Metadatos generales
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_data = [
        [Paragraph("<b>Fecha de Emisión:</b>", body_style), Paragraph(now_str, body_style)],
        [Paragraph("<b>Tipo de Peritaje:</b>", body_style), Paragraph("Identificación Lofoscópica / Dactilar", body_style)],
        [Paragraph("<b>Estatus Auditoría:</b>", body_style), Paragraph("Verificado por Segundo Examinador", bold_body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[130, 400])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. FASE A: ANÁLISIS
    story.append(Paragraph("1. FASE DE ANÁLISIS (ANALYSIS)", h2_style))
    
    total_a = len(data_a['minutiae']['terminations']) + len(data_a['minutiae']['bifurcations'])
    total_b = len(data_b['minutiae']['terminations']) + len(data_b['minutiae']['bifurcations'])

    analysis_data = [
        [Paragraph("Muestra", bold_body_style), Paragraph("Patrón Dactilar", bold_body_style), Paragraph("Terminaciones", bold_body_style), Paragraph("Bifurcaciones", bold_body_style), Paragraph("Total", bold_body_style)],
        [
            Paragraph("Huella A (Dudosa)", body_style),
            Paragraph(pattern_a, body_style),
            str(len(data_a['minutiae']['terminations'])),
            str(len(data_a['minutiae']['bifurcations'])),
            str(total_a)
        ],
        [
            Paragraph("Huella B (Referencia)", body_style),
            Paragraph(pattern_b, body_style),
            str(len(data_b['minutiae']['terminations'])),
            str(len(data_b['minutiae']['bifurcations'])),
            str(total_b)
        ],
    ]
    t_analysis = Table(analysis_data, colWidths=[130, 160, 80, 80, 80])
    t_analysis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_analysis)
    story.append(Spacer(1, 10))

    # 2. FASE C: COMPARACIÓN
    story.append(Paragraph("2. FASE DE COMPARACIÓN (COMPARISON)", h2_style))
    comp_data = [
        [Paragraph("<b>Umbral de Tolerancia Espacial:</b>", body_style), f"{match_result.get('threshold', 12)} píxeles"],
        [Paragraph("<b>Puntos Coincidentes (Minucias):</b>", body_style), f"{match_result['matches']} puntos"],
        [Paragraph("<b>Score de Similitud Cómputo:</b>", body_style), f"{match_result['score'] * 100:.2f}%"],
    ]
    t_comp = Table(comp_data, colWidths=[200, 330])
    t_comp.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # 3. FASE E: EVALUACIÓN
    story.append(Paragraph("3. FASE DE EVALUACIÓN (EVALUATION)", h2_style))

    decision_bg = colors.HexColor('#C6F6D5') if "IDENTIFICACIÓN" in evaluation['decision'] else (colors.HexColor('#FED7D7') if "EXCLUSIÓN" in evaluation['decision'] else colors.HexColor('#FEFCBF'))

    eval_data = [
        [Paragraph("<b>Dictamen Primario:</b>", bold_body_style), Paragraph(f"<b>{evaluation['decision']}</b>", bold_body_style)],
        [Paragraph("<b>Nivel de Confianza:</b>", body_style), Paragraph(evaluation['confidence'], body_style)],
        [Paragraph("<b>Fundamentación Técnica:</b>", body_style), Paragraph(evaluation['reason'], body_style)],
    ]
    t_eval = Table(eval_data, colWidths=[150, 380])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), decision_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_eval)
    story.append(Spacer(1, 10))

    # 4. FASE V: VERIFICACIÓN
    story.append(Paragraph("4. FASE DE VERIFICACIÓN (VERIFICATION)", h2_style))
    if audit_result:
        verif_data = [
            [Paragraph("<b>Perito Verificador:</b>", body_style), Paragraph(audit_result['verifier'], body_style)],
            [Paragraph("<b>Dictamen Auditoría:</b>", body_style), Paragraph(f"<b>{audit_result['verification_status']}</b>", bold_body_style)],
            [Paragraph("<b>Fecha/Hora Auditoría:</b>", body_style), Paragraph(audit_result['verification_time'], body_style)],
            [Paragraph("<b>Observaciones Periciales:</b>", body_style), Paragraph(audit_result['verifier_notes'] if audit_result['verifier_notes'] else "Sin observaciones adicionales.", body_style)],
        ]
    else:
        verif_data = [
            [Paragraph("<b>Estatus:</b>", body_style), Paragraph("Pendiente de verificación independiente por segundo perito.", body_style)]
        ]

    t_verif = Table(verif_data, colWidths=[150, 380])
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_verif)
    story.append(Spacer(1, 25))

    # Área de Firma Pericial
    signatures_data = [
        [
            Paragraph("________________________________________<br/><b>Firma del Perito Verificador</b><br/>" + (audit_result['verifier'] if audit_result else "Perito Acreditado"), ParagraphStyle('Sig', parent=body_style, alignment=1)),
        ]
    ]
    t_sig = Table(signatures_data, colWidths=[530])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    return buffer