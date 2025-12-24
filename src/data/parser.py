import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import date
from src.core.models import HorarioCrudo

class ParserInteligente:
    """Clase encargada de transformar texto plano y JSON en objetos de dominio HorarioCrudo"""
    def __init__(self):
        self.patron_titulo = re.compile(r'^([A-Z][A-Z\sÁÉÍÓÚÑ\-]+)$')
        
        self.patron_datos = re.compile(
            r'^([^\t]+)\t'    # Tipo
            r'([^\t]+)\t'     # Descripción
            r'([^\t]+)\t'     # Número curso
            r'([^\t]+)\t'     # Sección
            r'(\d+)\t'        # Créditos
            r'(\d+)\t'        # NRC
            r'([^\t]+)\t'     # Periodo
            r'([^\t]+)'       # Instructor
        )
        
        self.patron_horario = re.compile(
            r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s*'
            r'Tipo:\s*([A-ZÁÉÍÓÚÑ]+)\s*'
            r'Edificio:\s*(.+?)\s*'
            r'Salón:\s*(.+?)\s*'
            r'Fecha de inicio:\s*(.+?)\s*'
            r'Fecha de fin:\s*(.+?)$'
        )
        
        self.patron_cupos = re.compile(r'(\d+)\s*de\s*(\d+)\s*lugares\s*disponibles\.')
        self.patron_dia = re.compile(r'^(Lunes|Martes|Miércoles|Miercoles|Jueves|Viernes|Sábado|Sabado|Domingo)$', re.IGNORECASE)
        
        # Patrón Tabular Robusto: Soporta con y sin fechas intermedias
        self.patron_tabular = re.compile(
            r'(\d{4,6})\t'        # [1] NRC
            r'([^\t]+)\t'         # [2] Materia/Depto
            r'([^\t]+)\t'         # [3] N_Curso
            r'([^\t]+)\t'         # [4] Seccion
            r'([^\t]+)\t'         # [5] Componente/Tipo
            r'([^\t]+)\t'         # [6] Nombre Asignatura
            r'([^\t]*)\t'         # [7] Liga
            r'([^\t]*)\t'         # [8] Conector
            r'(\d+)\t'            # [9] Vacantes
            r'(?:(\d{2}-\d{2}-\d{4})\t(\d{2}-\d{2}-\d{4})\t)?' # [10,11] Fechas (OPCIONALES)
            r'([^\t]+)\t'         # [12] Sala/Ubicacion
            r'(\d{2,4})\t'        # [13] H_Ini
            r'(\d{2,4})'          # [14] H_Fin
        )

    def parsear_texto_por_prioridad(self, texto: str, prioridad: int) -> List[HorarioCrudo]:
        texto = texto.strip()
        if not texto: return []
        
        # 1. Intentar JSON
        if texto.startswith('[') or texto.startswith('{'):
            try:
                data = json.loads(texto)
                if isinstance(data, dict): data = [data]
                res = []
                for item in data:
                    res.append(HorarioCrudo(
                        nrc=str(item.get('nrc', '')), titulo=item.get('titulo', 'Sin Título'),
                        tipo=item.get('tipo', 'TEO'), seccion=item.get('seccion', 'T01'),
                        hora_str=item.get('hora', '00:00 - 00:00'), ubicacion=item.get('lugar', 'S/I'),
                        instructor=item.get('instructor', 'S/I'), campus="Principal",
                        cupos_disponibles=0, cupos_totales=0, es_ligado=False,
                        fecha_inicio=item.get('fecha_inicio', '02-03-2026'),
                        fecha_fin=item.get('fecha_fin', '11-07-2026'), prioridad=prioridad
                    ))
                if res: return res
            except: pass

        # 2. Intentar Tabular (Detección automática de sistema English/Spanish)
        resultados = self.parsear_texto_tabular(texto, prioridad)
        
        # 3. Fallback: Crudo
        if not resultados:
            resultados = self.parsear_texto_crudo(texto)
            for r in resultados: r.prioridad = prioridad

        # Deduplicación
        vistos = set()
        unicos = []
        for r in resultados:
            clave = (r.nrc, r.dia_parseado, r.hora_str, r.ubicacion)
            if clave not in vistos:
                vistos.add(clave)
                unicos.append(r)
        return unicos

    def parsear_texto_tabular(self, texto: str, prioridad: int) -> List[HorarioCrudo]:
        resultados = []
        texto = texto.replace('\r', '')
        
        # Detectar sistema: Si hay R (Thursday) o F (Friday), es English-style (M=Monday)
        es_ingles = bool(re.search(r'\t[RTFS]\t', texto)) or 'F' in texto or 'R' in texto
        
        mapping_en = {'M': 'Lunes', 'T': 'Martes', 'W': 'Miércoles', 'R': 'Jueves', 'F': 'Viernes', 'S': 'Sábado', 'U': 'Domingo'}
        mapping_es = {'L': 'Lunes', 'M': 'Martes', 'X': 'Miércoles', 'W': 'Miércoles', 'J': 'Jueves', 'V': 'Viernes', 'S': 'Sábado', 'D': 'Domingo'}
        mapping = mapping_en if es_ingles else mapping_es

        for match in self.patron_tabular.finditer(texto):
            g = match.groups()
            nrc, materia, ncurs, sec, tipo, nombre, liga, conec, vac, f_ini, f_fin, sala, h_ini, h_fin = g
            
            def fmt_h(h):
                h = h.replace(':', '').strip()
                if len(h) == 4: return f"{h[:2]}:{h[2:]}"
                if len(h) == 3: return f"0{h[0]}:{h[1:]}"
                return h
            
            # Días: Escaneamos tabs después del match
            pos_fin = match.end()
            fragmento = texto[pos_fin:pos_fin+250].split('\t')
            dia_detectado = None
            for seg in fragmento[:15]:
                s = seg.strip().upper()
                if s in mapping:
                    dia_detectado = mapping[s]
                    break
            
            if not dia_detectado:
                dia_detectado = self.calcular_dia_de_fecha(f_ini or "02-03-2026")

            resultados.append(HorarioCrudo(
                nrc=nrc, titulo=" ".join(nombre.split()).upper(), tipo=tipo.strip().upper(),
                seccion=sec.strip(), hora_str=f"{fmt_h(h_ini)} - {fmt_h(h_fin)}",
                ubicacion=sala.strip(), instructor="S/I", campus="Sede Principal",
                cupos_disponibles=int(vac) if vac and vac.isdigit() else 0,
                cupos_totales=int(vac) if vac and vac.isdigit() else 0,
                es_ligado=bool(liga.strip()), fecha_inicio=f_ini or "02-03-2026",
                fecha_fin=f_fin or "11-07-2026", dia_parseado=dia_detectado,
                prioridad=prioridad, liga=liga.strip(), conector=conec.strip()
            ))
        return resultados

    def parsear_texto_crudo(self, texto: str) -> List[HorarioCrudo]:
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        resultados = []
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            if linea.isupper() and len(linea) > 5 and 'TÍTULO' not in linea:
                titulo = linea
                i += 1
                while i < len(lineas) and '\t' not in lineas[i]: i += 1
                if i >= len(lineas): break
                m = self.patron_datos.search(lineas[i])
                if m:
                    tipo, _, _, sec, _, nrc, _, inst = m.groups()
                    i += 1
                    dia_act = None
                    while i < len(lineas) and 'lugares disponibles' not in lineas[i]:
                        dm = self.patron_dia.match(lineas[i])
                        if dm: dia_act = dm.group(1).title()
                        hm = self.patron_horario.search(lineas[i])
                        if hm:
                            hi, hf, _, ed, sa, fi, ff = hm.groups()
                            resultados.append(HorarioCrudo(
                                nrc=nrc, titulo=titulo, tipo=tipo, seccion=sec,
                                hora_str=f"{hi} - {hf}", ubicacion=f"{ed} {sa}",
                                instructor=inst, campus="Principal", cupos_disponibles=0,
                                cupos_totales=0, es_ligado=False, fecha_inicio=fi,
                                fecha_fin=ff, dia_parseado=dia_act
                            ))
                        i += 1
            i += 1
        return resultados

    def agrupar_por_nrc(self, horarios: List[HorarioCrudo]) -> Dict[str, List[HorarioCrudo]]:
        agrupados = {}
        for h in horarios:
            if h.nrc not in agrupados: agrupados[h.nrc] = []
            agrupados[h.nrc].append(h)
        return agrupados

    def calcular_dia_de_fecha(self, fecha_str: str) -> str:
        meses = {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12, 'Jan': 1, 'Mar': 3}
        dias_esp = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        try:
            p = fecha_str.split('-')
            if len(p) < 3: return "Lunes"
            m_str = p[1][:3].title()
            m_num = meses.get(m_str, 3)
            d = date(int(p[2]), m_num, int(p[0]))
            return dias_esp[d.weekday()]
        except: return "Lunes"