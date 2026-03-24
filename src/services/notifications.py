import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")


def _normalizar_asunto(asunto):
        asunto_limpio = (asunto or "Notificacion").strip()
        if asunto_limpio.startswith("🔔"):
                return asunto_limpio
        return f"🔔 ALUNA: {asunto_limpio}"


def _estado_visual(asunto, mensaje):
        texto = f"{asunto} {mensaje}".lower()

        if "completad" in texto:
                return "¡ENTREGA COMPLETADA!", "#27ae60"
        if "entrega" in texto or "recibida" in texto or "recibido" in texto:
                return "ENTREGA PARCIAL", "#e67e22"
        if "pago" in texto:
                return "PAGO REGISTRADO", "#16a085"
        if "auditor" in texto:
                return "AUDITORIA GENERADA", "#2c3e50"
        if "despacho" in texto:
                return "NUEVO DESPACHO", "#2980b9"
        if "trabajador" in texto or "usuario" in texto:
                return "NUEVO REGISTRO", "#8e44ad"

        return "NOTIFICACION DE OPERACION", "#2980b9"


def _contenido_html(mensaje):
        if not mensaje:
                return "<p>Sin detalles adicionales.</p>"

        if "<" in mensaje and ">" in mensaje:
                return mensaje

        return "<p>" + str(mensaje).replace("\n", "<br>") + "</p>"


def _plantilla_notificacion(asunto, mensaje):
        estado_texto, estado_color = _estado_visual(asunto, mensaje)
        contenido = _contenido_html(mensaje)

        return f"""
        <html>
            <body style="margin:0; padding:24px; background:#f1f3f5; font-family:Arial, Helvetica, sans-serif; color:#2f2f2f;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td align="center">
                            <table role="presentation" width="680" cellspacing="0" cellpadding="0" style="max-width:680px; background:#ffffff; border:1px solid #dfe3e8; border-radius:12px;">
                                <tr>
                                    <td style="padding:20px 20px 8px 20px;">
                                        <h2 style="margin:0; font-size:18px; color:#1f3042; font-weight:700;">🔔 ALUNA:</h2>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:0 20px 16px 20px;">
                                        <h3 style="margin:0; font-size:19px; color:#1f3042; font-weight:700;">Notificacion de Operacion</h3>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:0 20px 14px 20px;">
                                        <div style="height:2px; background:#2f8de4; width:100%;"></div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:0 20px 16px 20px;">
                                        <div style="background:{estado_color}; color:#ffffff; text-align:center; border-radius:6px; font-size:13px; font-weight:700; padding:12px 10px;">{estado_texto}</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:0 20px 20px 20px; font-size:11.5px; line-height:1.6;">
                                        {contenido}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:0 20px 0 20px;">
                                        <div style="height:1px; background:#e5e7eb; width:100%;"></div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:18px 20px 24px 20px; text-align:center; color:#9aa0a6; font-size:7px;">
                                        Sistema ALUNA - Gestion Automatica
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

def enviar_notificacion_async(asunto, mensaje):
    """Envía notificación por email en un thread aparte"""
    thread = threading.Thread(target=enviar_notificacion, args=(asunto, mensaje))
    thread.daemon = True
    thread.start()

def enviar_notificacion(asunto, mensaje):
    """Envía notificación por email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMITENTE
        msg['To'] = EMAIL_DESTINO
        msg['Subject'] = _normalizar_asunto(asunto)

        body = _plantilla_notificacion(asunto, mensaje)
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error al enviar email: {e}")

def enviar_notificacion_entrega(trabajador, referencia, recibida, total_despachado, acumulado):
    """Notificación específica de entrega recibida"""
    es_completada = acumulado >= total_despachado
    pendiente = max(total_despachado - acumulado, 0)

    if es_completada:
        asunto = f"Entrega Completada - {trabajador}"
        resumen = "<p>El trabajador ha entregado la totalidad del material.</p>"
    else:
        asunto = f"Entrega Parcial - {trabajador}"
        resumen = f"<p>Aun quedan <b>{pendiente} unidades pendientes</b> por entregar.</p>"

    mensaje = f"""
        <p>Hola, se ha registrado una entrada de material:</p>
        <ul>
            <li><b>Trabajador:</b> {trabajador}</li>
            <li><b>Referencia:</b> {referencia}</li>
            <li><b>Cantidad recibida hoy:</b> {recibida} und.</li>
        </ul>
        {resumen}
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse; margin-top:8px;">
            <tr>
                <th style="border:1px solid #e5e7eb; background:#f7f7f7; padding:8px;">Despachado</th>
                <th style="border:1px solid #e5e7eb; background:#f7f7f7; padding:8px;">Recibido Total</th>
            </tr>
            <tr>
                <td style="border:1px solid #e5e7eb; text-align:center; padding:10px;">{total_despachado}</td>
                <td style="border:1px solid #e5e7eb; text-align:center; padding:10px;">{acumulado}</td>
            </tr>
        </table>
    """
    enviar_notificacion_async(asunto, mensaje)
