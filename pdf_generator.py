"""
Módulo de generación de reportes ejecutivos en PDF y Excel para auditorías de inventario.
Utiliza ReportLab para generar un archivo PDF profesional con formato formal,
tablas resumidas, desglose de faltantes y firmas de auditoría.
"""

import os
from typing import List, Dict, Any
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

from inventory_model import InventoryManager, InventoryItem


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para agregar números de página 'Página X de Y' y pie de página.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Línea de pie de página
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 36, self._pagesize[0] - 36, 36)

        # Texto pie de página
        footer_text = "Sistema de Control de Inventarios Mensuales - Reporte Oficial de Auditoría"
        page_text = f"Página {self._pageNumber} de {page_count}"

        self.drawString(36, 22, footer_text)
        self.drawRightString(self._pagesize[0] - 36, 22, page_text)
        self.restoreState()


class InventoryReportGenerator:
    """
    Generador de reportes en Excel y PDF para el sistema de inventarios.
    """

    @staticmethod
    def export_to_excel(inventory_mgr: InventoryManager, output_path: str) -> str:
        """
        Exporta el inventario completo a un archivo Excel (.xlsx) estilizado.
        """
        df = inventory_mgr.to_dataframe()

        # Si el DataFrame está vacío, crear estructura básica
        if df.empty:
            df = pd.DataFrame(columns=[
                "Código/SKU", "Descripción", "Categoría",
                "Stock Teórico", "Stock Físico", "Diferencia",
                "Estatus", "Ruta Evidencia", "Nuevo"
            ])

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Inventario Mensual', index=False)

            # Obtener hoja para formato
            workbook = writer.book
            worksheet = writer.sheets['Inventario Mensual']

            # Ajustar ancho de columnas automáticamente
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        return output_path

    @staticmethod
    def export_to_pdf(inventory_mgr: InventoryManager, output_path: str, title: str = "Reporte Ejecutivo de Inventario Mensual") -> str:
        """
        Genera un reporte PDF profesional estilo auditoría.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Configuración de página en orientación horizontal (Landscape) para mejor lectura de tabla
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=50
        )

        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1A365D'),
            alignment=0, # Izquierda
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=15
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#2C5282'),
            spaceBefore=15,
            spaceAfter=8
        )

        normal_body = ParagraphStyle(
            'NormalBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#2D3748')
        )

        table_header = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=1 # Centrado
        )

        table_cell = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1A202C')
        )

        table_cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=table_cell,
            alignment=1
        )

        # --- ENCABEZADO ---
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(f"Fecha de generación: <b>{fecha_actual}</b> | Estado de auditoría: <b>COMPLETADO</b>", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2B6CB0'), spaceAfter=15))

        # --- RESUMEN EJECUTIVO (KPIs) ---
        all_items = inventory_mgr.get_all_items()
        total_items = len(all_items)
        total_teorico = sum(item.theoretical_stock for item in all_items)
        total_fisico = sum(item.physical_stock for item in all_items)

        faltantes = [item for item in all_items if item.status == "Faltante"]
        excedentes = [item for item in all_items if item.status == "Excedente"]
        nuevos = [item for item in all_items if item.is_new_item or item.status == "Nuevo fuera de catálogo"]
        en_regla = [item for item in all_items if item.status == "En inventario"]

        kpi_data = [
            [
                Paragraph("<b>Total SKUs Registrados</b>", table_cell_center),
                Paragraph("<b>Stock Teórico Total</b>", table_cell_center),
                Paragraph("<b>Stock Físico Total</b>", table_cell_center),
                Paragraph("<b>Items Faltantes</b>", table_cell_center),
                Paragraph("<b>Items Nuevos</b>", table_cell_center)
            ],
            [
                Paragraph(f"<font size=12><b>{total_items}</b></font>", table_cell_center),
                Paragraph(f"<font size=12><b>{total_teorico:g}</b></font>", table_cell_center),
                Paragraph(f"<font size=12><b>{total_fisico:g}</b></font>", table_cell_center),
                Paragraph(f"<font size=12 color='#C53030'><b>{len(faltantes)}</b></font>", table_cell_center),
                Paragraph(f"<font size=12 color='#2B6CB0'><b>{len(nuevos)}</b></font>", table_cell_center)
            ]
        ]

        kpi_table = Table(kpi_data, colWidths=[140, 140, 140, 140, 140])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F7FAFC')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(Paragraph("Resumen General de Auditoría", section_heading))
        elements.append(kpi_table)
        elements.append(Spacer(1, 15))

        # --- TABLA DETALLADA DE INVENTARIO ---
        elements.append(Paragraph("Detalle Completo de Inventario", section_heading))

        headers = ["Código / SKU", "Descripción", "Categoría", "Teórico", "Físico", "Dif.", "Estatus", "Evidencia"]
        col_widths = [80, 180, 100, 55, 55, 45, 110, 85]

        table_rows = [[Paragraph(h, table_header) for h in headers]]

        for item in all_items:
            # Color de estatus
            status_color = "#2D3748"
            if item.status == "Faltante":
                status_color = "#C53030" # Rojo
            elif item.status == "Excedente":
                status_color = "#DD6B20" # Naranja
            elif item.status == "Nuevo fuera de catálogo":
                status_color = "#3182CE" # Azul
            elif item.status == "En inventario":
                status_color = "#38A169" # Verde

            evidencia_str = "Con foto" if item.photo_path and os.path.exists(item.photo_path) else "Sin foto"

            table_rows.append([
                Paragraph(f"<b>{item.sku}</b>", table_cell),
                Paragraph(item.description, table_cell),
                Paragraph(item.category, table_cell),
                Paragraph(f"{item.theoretical_stock:g}", table_cell_center),
                Paragraph(f"{item.physical_stock:g}", table_cell_center),
                Paragraph(f"{item.difference:+g}", table_cell_center),
                Paragraph(f"<font color='{status_color}'><b>{item.status}</b></font>", table_cell_center),
                Paragraph(evidencia_str, table_cell_center)
            ])

        inv_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(inv_table)
        elements.append(Spacer(1, 20))

        # --- SECCIÓN DE FIRMAS Y CONFORMIDAD ---
        signature_data = [
            [
                Paragraph("___________________________________<br/><b>Auditor / Realizó Conteo</b>", table_cell_center),
                Paragraph("___________________________________<br/><b>Gerente de Almacén / Conformidad</b>", table_cell_center)
            ]
        ]
        sig_table = Table(signature_data, colWidths=[350, 350])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
        ]))

        elements.append(KeepTogether([
            Paragraph("Firmas de Autorización y Conformidad", section_heading),
            Spacer(1, 10),
            sig_table
        ]))

        # Construir PDF usando NumberedCanvas
        doc.build(elements, canvasmaker=NumberedCanvas)
        return output_path
