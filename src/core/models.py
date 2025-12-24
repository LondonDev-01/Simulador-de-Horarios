from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class HorarioCrudo:
    """Representa un bloque de horario extraído directamente de la fuente (sin procesar día de la semana)"""
    nrc: str
    titulo: str
    tipo: str  # "TEO", "LAB", "TALLER", etc.
    seccion: str
    hora_str: str  # Ejemplo: "14:40 - 16:00"
    ubicacion: str
    instructor: str
    campus: str
    cupos_disponibles: int
    cupos_totales: int
    es_ligado: bool
    fecha_inicio: str
    fecha_fin: str
    dia_parseado: Optional[str] = None
    prioridad: int = 0  # 0: Obligatorio, 1: Adelantar, 2: Electivo
    liga: str = ""
    conector: str = ""

@dataclass
class ClaseConDia:
    """Representa una sesión de clase con el día de la semana ya asignado y horas normalizadas"""
    nrc: str
    titulo: str
    tipo: str
    seccion: str
    dia: str  # Lunes, Martes...
    hora_inicio: str
    hora_fin: str
    minutos_inicio: int
    minutos_fin: int
    edificio: str
    salon: str
    instructor: str
    fecha_inicio: str
    prioridad: int = 0
    liga: str = ""
    conector: str = ""
