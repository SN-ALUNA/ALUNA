from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UsuarioDTO:
    id: str
    nombre_full: str
    telefono: str
    rol_trabajo: str
    created_at: Optional[datetime] = None

@dataclass
class ProductoDTO:
    id: str
    nombre_ref: str
    categoria: str
    valor_unitario: float
    stock_total: int
    stock_en_calle: int
    stock_terminado: int
    created_at: Optional[datetime] = None

@dataclass
class DespachoDTO:
    id: str
    usuario_id: str
    producto_id: str
    cant_despachada: int
    cant_entregada: int
    fecha_salida: str
    valor_total_esperado: float
    valor_pagado_real: float
    estado: str
    estado_pago: str
    created_at: Optional[datetime] = None

@dataclass
class CalendarioPagoDTO:
    id: str
    fecha_programada: str
    categoria: str
    descripcion: str
    estado: str
    created_at: Optional[datetime] = None
