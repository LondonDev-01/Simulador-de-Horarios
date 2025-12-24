from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from typing import List
from src.core.models import ClaseConDia

class ExcelExporter:
    """Servicio encargado de renderizar y exportar horarios a formato Excel Premium"""
    
    COLORES_EXCEL = ["BFDBFE", "BBF7D0", "FEF3C7", "FECACA", "DDD6FE", "F5D0FE", "FED7AA"]
    DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

    @staticmethod
    def exportar(clases: List[ClaseConDia], nombre_archivo: str):
        wb = Workbook()
        ws = wb.active
        ws.title = "Horario Optimizado"
        
        # --- TABLA RESUMEN ---
        headers = ["NRC", "Asignatura", "Tipo", "Sección", "Día", "Horario", "Docente"]
        ws.append(headers)
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.font, cell.fill = header_font, header_fill
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[get_column_letter(col)].width = 15
        
        ws.column_dimensions['B'].width = 30
        
        # Llenar datos de ramos
        for i, c in enumerate(clases, 2):
            ws.cell(row=i, column=1, value=c.nrc)
            ws.cell(row=i, column=2, value=c.titulo)
            ws.cell(row=i, column=3, value=c.tipo)
            ws.cell(row=i, column=4, value=c.seccion)
            ws.cell(row=i, column=5, value=c.dia)
            ws.cell(row=i, column=6, value=f"{c.hora_inicio} - {c.hora_fin}")
            ws.cell(row=i, column=7, value=c.instructor)
            
            for col in range(1, 8):
                ws.cell(row=i, column=col).border = Border(bottom=Side(style='thin'))

        # --- GRILLA SEMANAL ---
        start_row = len(clases) + 5
        ws.cell(row=start_row-1, column=1, value="MAPA SEMANAL").font = Font(size=14, bold=True)
        
        # Headers de días
        for i, dia in enumerate(ExcelExporter.DIAS_SEMANA):
            cell = ws.cell(row=start_row, column=2 + i, value=dia)
            cell.font, cell.alignment = Font(bold=True), Alignment(horizontal="center")
            cell.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
            ws.column_dimensions[get_column_letter(2+i)].width = 20

        # Filas de horas
        row_map = {}
        for i, h in enumerate(range(8, 23)):
            row = start_row + 1 + i
            ws.cell(row=row, column=1, value=f"{h:02d}:00").font = Font(bold=True)
            row_map[h] = row
            for d in range(6):
                ws.cell(row=row, column=2+d).border = Border(left=Side(style='dotted'), bottom=Side(style='dotted'))

        # Bloquear celdas con ramos
        nrc_colors = {}
        idx_color = 0
        for c in clases:
            if c.nrc not in nrc_colors:
                nrc_colors[c.nrc] = ExcelExporter.COLORES_EXCEL[idx_color % len(ExcelExporter.COLORES_EXCEL)]
                idx_color += 1
            
            fill = PatternFill(start_color=nrc_colors[c.nrc], end_color=nrc_colors[c.nrc], fill_type="solid")
            try:
                h_start = int(c.hora_inicio.split(':')[0])
                h_end = int(c.hora_fin.split(':')[0])
                if c.dia in ExcelExporter.DIAS_SEMANA:
                    col_idx = 2 + ExcelExporter.DIAS_SEMANA.index(c.dia)
                    rango = range(h_start, h_end + (1 if int(c.hora_fin.split(':')[1]) > 0 else 0))
                    for h in rango:
                        if h in row_map:
                            cell = ws.cell(row=row_map[h], column=col_idx)
                            cell.fill = fill
                            if h == h_start:
                                cell.value = f"{c.titulo}\n({c.nrc})"
                                cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            except: pass
        
        wb.save(nombre_archivo)