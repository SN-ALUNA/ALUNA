from src.database.supabase_client import supabase
from datetime import datetime

class UsuariosRepository:
    @staticmethod
    def obtener_todos():
        res = supabase.table("usuarios").select("*").execute()
        return res.data
    
    @staticmethod
    def obtener_por_id(user_id):
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else None
    
    @staticmethod
    def crear(nombre_full, telefono, rol_trabajo):
        res = supabase.table("usuarios").insert({
            "nombre_full": nombre_full,
            "telefono": telefono,
            "rol_trabajo": rol_trabajo
        }).execute()
        return res.data

class ProductosRepository:
    @staticmethod
    def obtener_todos():
        res = supabase.table("productos").select("*").execute()
        return res.data
    
    @staticmethod
    def obtener_por_categoria(categoria):
        res = supabase.table("productos").select("*").eq("categoria", categoria).execute()
        return res.data
    
    @staticmethod
    def crear(nombre_ref, categoria, valor_unitario, stock_total):
        res = supabase.table("productos").insert({
            "nombre_ref": nombre_ref,
            "categoria": categoria,
            "valor_unitario": valor_unitario,
            "stock_total": stock_total,
            "stock_en_calle": 0,
            "stock_terminado": 0
        }).execute()
        return res.data

class DespachosRepository:
    @staticmethod
    def obtener_todos():
        res = supabase.table("despachos").select("*, usuarios(*), productos(*)").execute()
        return res.data
    
    @staticmethod
    def obtener_pendientes():
        res = supabase.table("despachos").select("*, usuarios(*), productos(*)").eq("estado", "pendiente").execute()
        return res.data
    
    @staticmethod
    def crear(usuario_id, producto_id, cant_despachada, valor_total_esperado):
        res = supabase.table("despachos").insert({
            "usuario_id": usuario_id,
            "producto_id": producto_id,
            "cant_despachada": cant_despachada,
            "cant_entregada": 0,
            "fecha_salida": datetime.now().strftime("%Y-%m-%d"),
            "valor_total_esperado": valor_total_esperado,
            "valor_pagado_real": 0,
            "estado": "pendiente",
            "estado_pago": "pendiente"
        }).execute()
        return res.data

class CalendarioPagosRepository:
    @staticmethod
    def obtener_por_mes(year, month):
        inicio = f"{year}-{month:02d}-01"
        from calendar import monthrange
        ultimo_dia = monthrange(year, month)[1]
        fin = f"{year}-{month:02d}-{ultimo_dia}"
        res = supabase.table("calendario_pagos").select("*").gte("fecha_programada", inicio).lte("fecha_programada", fin).execute()
        return res.data
    
    @staticmethod
    def crear(fecha_programada, categoria, descripcion):
        res = supabase.table("calendario_pagos").insert({
            "fecha_programada": fecha_programada,
            "categoria": categoria,
            "descripcion": descripcion,
            "estado": "pendiente"
        }).execute()
        return res.data
