from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Token del bot
TOKEN = "8238726820:AAGU_CouD4wXuxMDMjloF76NiC3LjsPdwRY"  # ← Reemplaza esto por tu token real

CHAT_ID_GLOBAL = None

# Stickers opcionales (puedes comentar estas líneas si no los usas)
STICKER_HIMNO = ""
STICKER_GUARDIA = ""

# Registro de llegadas
registro_llegadas = {
    "media_tarde": 0,
    "muy_tarde": 0
}

scheduler = BackgroundScheduler()
scheduler.start()

# Operadores por día (0 = lunes, 6 = domingo)
OPERADORES = {
    0: ["Oscar", "Josep"],
    1: ["Coral", "Estefani"],
    2: ["José", "Sinaí"],
    3: ["Daverson", "Meralis"],
    4: ["Genesis Zapata"],
    5: ["Jesús Olivo"],
    6: ["Víctor Ramírez"]
}

MENSAJES_DIARIOS = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

FECHAS_PATRIAS = {
    "04-19": "19 de Abril",
    "07-05": "5 de Julio",
    "03-28": "Nacimiento de Miranda"
}

RECORDATORIOS_DIARIOS = [
    ("06:00", "Himno matutino"),
    ("10:00", "Guardia en puerta"),
    ("12:00", "Reglas generales"),
    ("18:00", "Cierre de jornada"),
    ("00:00", "Himno nocturno")
]

def enviar_recordatorio_programado(mensaje, sticker=None):
    if CHAT_ID_GLOBAL:
        app.bot.send_message(chat_id=CHAT_ID_GLOBAL, text=mensaje)
        if sticker:
            app.bot.send_sticker(chat_id=CHAT_ID_GLOBAL, sticker=sticker)

def programar_recordatorios_diarios():
    for hora_str, mensaje in RECORDATORIOS_DIARIOS:
        hora, minuto = map(int, hora_str.split(":"))
        sticker = None
        scheduler.add_job(
            enviar_recordatorio_programado,
            "cron",
            hour=hora,
            minute=minuto,
            args=[mensaje, sticker]
        )

programar_recordatorios_diarios()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID_GLOBAL
    CHAT_ID_GLOBAL = update.effective_chat.id
    dia = datetime.datetime.now().weekday()
    saludo = MENSAJES_DIARIOS.get(dia)
    fecha = datetime.datetime.now().strftime("%m-%d")
    mensaje = FECHAS_PATRIAS.get(fecha, saludo)
    await update.message.reply_text(
        f"{mensaje}\n\nBot activo."
    )

async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hora = context.args[0]
        mensaje = " ".join(context.args[1:]) if len(context.args) > 1 else "Recordatorio automático"
        hora_obj = datetime.datetime.strptime(hora, "%H:%M")
        ahora = datetime.datetime.now()
        fecha_obj = ahora.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0)
        if fecha_obj < ahora:
            fecha_obj += datetime.timedelta(days=1)
        scheduler.add_job(enviar_recordatorio_programado, 'date', run_date=fecha_obj, args=[mensaje])
        await update.message.reply_text(f"Recordatorio para {hora}: {mensaje}")
    except:
        await update.message.reply_text("Usa el formato: /recordar HH:MM mensaje")

async def reglas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = """Reglas del grupo:

1\. Respeto
2\. Puntualidad
3\. Orden técnico
4\. Entrega creativa"""
    await update.message.reply_text(texto)

async def llegadas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media = registro_llegadas.get("media_tarde", 0)
    muy = registro_llegadas.get("muy_tarde", 0)
    await update.message.reply_text(f"Media hora tarde: {media} veces\nMuy tarde: {muy} veces"
    )

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    await update.message.reply_text(
        f"Bot activo — {fecha}"
    )

FRAGMENTOS_GUARDIA = [
    "guardia entregada a", "se entrega guardia a",
    "se le entrega guardia a la compañera", "se le entrega guardia al compañero",
    "se estrega guardia al compañero", "se estrega guardia a la compañera"
]

async def detectar_guardia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID_GLOBAL
    if not CHAT_ID_GLOBAL:
        CHAT_ID_GLOBAL = update.effective_chat.id
    texto = update.message.text.lower()
    if any(frag in texto for frag in FRAGMENTOS_GUARDIA):
        dia = datetime.datetime.now().weekday()
        hora_actual = datetime.datetime.now().time()
        nombres = OPERADORES.get(dia, [])
        mensaje = f"Guardia recibida: {', '.join(nombres)}"
        if hora_actual >= datetime.time(10, 31) and hora_actual < datetime.time(11, 0):
            mensaje += "\nLlegaste media hora tarde."
            registro_llegadas["media_tarde"] += 1
        elif hora_actual >= datetime.time(11, 0):
            mensaje += "\nLlegaste muy tarde."
            registro_llegadas["muy_tarde"] += 1
        else:
            mensaje += "\nGuardia dentro del tiempo."
        await update.message.reply_text(mensaje)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("recordar", recordar))
app.add_handler(CommandHandler("reglas", reglas))
app.add_handler(CommandHandler("llegadas", llegadas))
app.add_handler(CommandHandler("estado", estado))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detectar_guardia))

app.run_polling()

