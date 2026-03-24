from datetime import datetime

def formatear_fecha(fecha_str):
    """Convierte string de fecha a formato legible"""
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        return fecha.strftime("%d de %B de %Y")
    except:
        return fecha_str

def formatear_moneda(monto):
    """Formatea monto a formato de moneda"""
    return f"${monto:,.2f}"

def validar_fecha(fecha_str):
    """Valida que una fecha esté en formato correcto"""
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except:
        return False
