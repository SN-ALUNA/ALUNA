from src.database.repositories import UsuariosRepository
from src.services.notifications import enviar_notificacion_async

class UsuarioService:
    @staticmethod
    def obtener_todos():
        return UsuariosRepository.obtener_todos()
    
    @staticmethod
    def obtener_por_id(user_id):
        return UsuariosRepository.obtener_por_id(user_id)
    
    @staticmethod
    def crear_usuario(nombre_full, telefono, rol_trabajo):
        usuario = UsuariosRepository.crear(nombre_full, telefono, rol_trabajo)
        enviar_notificacion_async(
            "Nuevo Trabajador Registrado",
            f"Se ha registrado a <b>{nombre_full}</b> en el área de {rol_trabajo.upper()}."
        )
        return usuario
