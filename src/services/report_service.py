from src.database.supabase_client import supabase

class ReportService:
    @staticmethod
    def obtener_reporte_trabajador(usuario_id):
        """Obtiene el reporte de un trabajador (despachos pendientes)"""
        try:
            res = supabase.table("despachos").select("*, usuarios(*), productos(*)").eq("usuario_id", usuario_id).execute()
            return res.data
        except Exception as e:
            print(f"Error al obtener reporte: {e}")
            return []
    
    @staticmethod
    def obtener_reporte_general():
        """Obtiene reporte general de todos los despachos"""
        try:
            res = supabase.table("despachos").select("*, usuarios(*), productos(*)").execute()
            return res.data
        except Exception as e:
            print(f"Error al obtener reporte general: {e}")
            return []
