from datetime import datetime
from db import obtener_datos, guardar_logros

def revisar_logros(user_id):
    mensajes, reacciones, tiempo_ingreso, logros_guardados = obtener_datos(user_id)
    nuevos = []

    if mensajes >= 1:
        nuevos.append("🧠 Mentat desmemoriad@")
    if mensajes >= 100:
        nuevos.append("💬 Muad'Dib del Chat")
    if mensajes >= 1000:
        nuevos.append("🧠 Mentat del Foro")
    if reacciones >= 1:
        nuevos.append("💛 Novat@ en la Prescencia")
    if reacciones >= 20:
        nuevos.append("🎭 Fremen Popular")
    if tiempo_ingreso:
        dias = (datetime.now() - datetime.fromisoformat(tiempo_ingreso)).days
        if dias >= 30:
            nuevos.append("📅 Fremen del Sietch")
    if tiempo_ingreso:
        dias = (datetime.now() - datetime.fromisoformat(tiempo_ingreso)).days
        if dias >= 1:
            nuevos.append("📅 Trucha de Arena Recién Nacida")

    return guardar_logros(user_id, nuevos)
