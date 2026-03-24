from src.database.repositories import DespachosRepository
from src.services.notifications import enviar_notificacion_async

class DespachoService:
    @staticmethod
    def obtener_todos():
        return DespachosRepository.obtener_todos()
    
    @staticmethod
    def obtener_pendientes():
        return DespachosRepository.obtener_pendientes()
    
    @staticmethod
    def crear_despacho(usuario_id, producto_id, cant_despachada, valor_total_esperado):
        despacho = DespachosRepository.crear(usuario_id, producto_id, cant_despachada, valor_total_esperado)
        enviar_notificacion_async(
            "Nuevo Despacho",
            f"Se entregaron <b>{cant_despachada}</b> unidades."
        )
        return despacho
