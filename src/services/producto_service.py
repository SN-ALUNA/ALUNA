from src.database.repositories import ProductosRepository
from src.services.notifications import enviar_notificacion_async

class ProductoService:
    @staticmethod
    def obtener_todos():
        return ProductosRepository.obtener_todos()
    
    @staticmethod
    def obtener_por_categoria(categoria):
        return ProductosRepository.obtener_por_categoria(categoria)
    
    @staticmethod
    def crear_producto(nombre_ref, categoria, valor_unitario, stock_total):
        producto = ProductosRepository.crear(nombre_ref, categoria, valor_unitario, stock_total)
        enviar_notificacion_async(
            "Nueva Referencia",
            f"Se creó la referencia <b>{nombre_ref}</b> con {stock_total} unidades."
        )
        return producto
    
    @staticmethod
    def incrementar_stock(producto_id, cantidad):
        producto = ProductosRepository.obtener_por_id(producto_id) if hasattr(ProductosRepository, 'obtener_por_id') else None
        if producto:
            nuevo_stock = producto['stock_total'] + cantidad
            enviar_notificacion_async(
                "Reabastecimiento Bodega",
                f"Ingreso de {cantidad} unidades. Total: {nuevo_stock}"
            )
