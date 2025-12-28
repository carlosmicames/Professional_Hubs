# conflict_api/app/services/pdf_generator.py
"""
Servicio para generar PDFs de resúmenes de intake.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

from app.models.intake import IntakeCall


def generar_pdf_intake_call(intake_call: IntakeCall) -> bytes:
    """
    Genera PDF con resumen de llamada de intake.
    
    Args:
        intake_call: Objeto IntakeCall con la información
    
    Returns:
        Bytes del PDF generado
    """
    # Crear buffer en memoria
    buffer = io.BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Estilo para secciones
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("RESUMEN DE LLAMADA DE INTAKE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Número de caso
    story.append(Paragraph(f"<b>Caso #:</b> {intake_call.id}", styles['Normal']))
    story.append(Paragraph(
        f"<b>Fecha:</b> {intake_call.creado_en.strftime('%d/%m/%Y %H:%M')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Información del Cliente
    story.append(Paragraph("INFORMACIÓN DEL CLIENTE", section_style))
    
    cliente_data = [
        ['Nombre Completo:', intake_call.nombre_completo or 'No proporcionado'],
        ['Teléfono:', intake_call.telefono_contacto or intake_call.numero_llamante],
        ['Email:', intake_call.email or 'No proporcionado'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(cliente_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Información del Caso
    story.append(Paragraph("INFORMACIÓN DEL CASO", section_style))
    
    # Tipo de caso con color según urgencia
    urgencia_color = {
        'emergencia': colors.red,
        'alta': colors.orange,
        'media': colors.yellow,
        'baja': colors.green
    }.get(intake_call.urgencia.value if intake_call.urgencia else 'media', colors.grey)
    
    caso_data = [
        ['Tipo de Caso:', (intake_call.tipo_caso.value if intake_call.tipo_caso else 'No especificado').upper()],
        ['Urgencia:', f'<font color="{urgencia_color}">{(intake_call.urgencia.value if intake_call.urgencia else "media").upper()}</font>'],
        ['Estado:', (intake_call.estado.value if intake_call.estado else 'en_progreso').upper()],
    ]
    
    caso_table = Table(caso_data, colWidths=[2*inch, 4*inch])
    caso_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(caso_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Descripción del Caso
    story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", section_style))
    descripcion = intake_call.descripcion_caso or "Sin descripción proporcionada."
    story.append(Paragraph(descripcion, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Información Adicional
    if intake_call.fuente_referido or intake_call.notas_adicionales:
        story.append(Paragraph("INFORMACIÓN ADICIONAL", section_style))
        
        if intake_call.fuente_referido:
            story.append(Paragraph(
                f"<b>Referido por:</b> {intake_call.fuente_referido}",
                styles['Normal']
            ))
        
        if intake_call.notas_adicionales:
            story.append(Paragraph(
                f"<b>Notas:</b> {intake_call.notas_adicionales}",
                styles['Normal']
            ))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Acción Requerida
    story.append(Paragraph("ACCIÓN REQUERIDA", section_style))
    
    if intake_call.urgencia and intake_call.urgencia.value in ['emergencia', 'alta']:
        accion = "⚠️ <b>ATENCIÓN URGENTE</b> - Contactar al cliente hoy mismo"
        story.append(Paragraph(accion, styles['Normal']))
    else:
        accion = "Contactar al cliente en 1-2 días hábiles"
        story.append(Paragraph(accion, styles['Normal']))
    
    # Verificación de conflictos
    if intake_call.conflicto_verificado:
        story.append(Paragraph("✓ Verificación de conflictos completada", styles['Normal']))
    else:
        story.append(Paragraph(
            "⚠️ <b>PENDIENTE:</b> Verificar conflictos de interés antes de aceptar el caso",
            styles['Normal']
        ))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"Professional Hubs © {datetime.now().year} | Documento generado automáticamente",
        footer_style
    ))
    
    # Construir PDF
    doc.build(story)
    
    # Obtener bytes del PDF
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes