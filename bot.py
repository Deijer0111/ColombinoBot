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

# 🔐 Token de tu bot
TOKEN = "8238726820:AAGU_CouD4wXuxMDMjloF76NiC3LjsPdwRY"  # ← Reemplaza esto con tu token de BotFather

# 🧠 Se activa automáticamente con /start
CHAT_ID_GLOBAL = None

# 🎟️ Stickers (puedes reemplazar los file_id por otros tuyos)
STICKER_HIMNO = "CAACAgEAAxkBAAECvXpkX4cNmxGhXLbHiKJO-HvYOjsLVgACNAEAAstxAAFWdFhgfFXEVi8E"
STICKER_GUARDIA = "CAACAgEAAxkBAAECvX5kX4cltvXQDjJmKwxWTR2LrCh5iAACVAEAAstxAAFnzPfIPgR-YC8E"

# 📊 Registro de llegadas
registro_llegadas = {
    "media_tarde": 0,
    "muy_tarde": 0
}

# ⏱️ Inicializar programador
scheduler = BackgroundScheduler()
scheduler.start()

# 📆 Operadores por día (lunes=0 ... domingo=6)
OPERADORES = {
    0: ["Oscar", "Josep"],
    1: ["Coral", "Estefani"],
    2: ["José", "Sinaí"],
    3: ["Daverson", "Meralis"],
    4: ["Genesis Zapata"],
    5: ["Jesús Olivo"],
    6: ["Víctor Ramírez"]
}

# 🗓️ Frases por día
MENSAJES_DIARIOS = {
    0: "💪 *Lunes de arranque* — ¡Máster activo con fuerza!",
    1: "🛠️ *Martes técnico* — Revisa el audio y respira producción.",
    2: "📚 *Miércoles pedagógico* — Formación con firmeza.",
    3: "🎨 *Jueves creativo* — Que fluya la edición.",
    4: "🎬 *Viernes de cierre* — Cámara en alto.",
    5: "🌞 *Sábado educativo* — Cultura no descansa.",
    6: "🕊️ *Domingo reflexivo* — Semana de agradecimiento."
}

# 📅 Fechas patrias reconocidas
FECHAS_PATRIAS = {
    "04-19": "📅 *19 de Abril* — Comienzo de la Independencia 🇻🇪",
    "07-05": "📅 *5 de Julio* — Firma del Acta 🎉",
    "03-28": "📜 *Nacimiento de Miranda* — Honor al Precursor."
}

# 🕒 Recordatorios automáticos
RECORDATORIOS_DIARIOS = [
    ("06:00", "🎶 *Himno Nacional* — ¡Que suene la dignidad! 🇻🇪"),
    ("10:00", "🛡️ *Guardia en puerta* — Producción lista."),
    ("12:00", "📘 *Reglas Máster* — Respeto y entrega."),
    ("18:00", "🎬 *Cierre de jornada* — ¡Gracias equipo!"),
    ("00:00", "🌙 *Himno nocturno* — Descanso con orgullo.")
]

# 📩 Enviar mensaje automático
def enviar_recordatorio_programado(mensaje, sticker=None):
    if CHAT_ID_GLOBAL:
        app.bot.send_message(chat_id=CHAT_ID_GLOBAL, text=mensaje, parse_mode="Markdown")
        if sticker:
            app.bot.send_sticker(chat_id=CHAT_ID_GLOBAL, sticker=sticker)

# 📌 Programar mensajes diarios
def programar_recordatorios_diarios():
    for hora_str, mensaje in RECORDATORIOS_DIARIOS:
        hora, minuto = map(int, hora_str.split(":"))
        sticker = None
        if "Himno" in mensaje:
            sticker = STICKER_HIMNO
        elif "Guardia" in mensaje:
            sticker = STICKER_GUARDIA
        scheduler.add_job(enviar_recordatorio_programado, "cron", hour=hora, minute=minute, args=[mensaje, sticker])

programar_recordatorios_diarios()

# 🔰 Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID_GLOBAL
    CHAT_ID_GLOBAL = update.effective_chat.id
    dia = datetime.datetime.now().weekday()
    saludo = MENSAJES_DIARIOS.get(dia)
    fecha = datetime.datetime.now().strftime("%m-%d")
    mensaje = FECHAS_PATRIAS.get(fecha, saludo)
    await update.message.reply_text(
        f"{mensaje}\n\n🦜 *ColombinoBot activo* para el Máster educativo.\nUsa `/recordar HH:MM mensaje`, `/reglas`, o `/llegadas`.",
        parse_mode="Markdown"
    )

# ⏰ Comando /recordar
async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hora = context.args[0]
        mensaje = " ".join(context.args[1:]) if len(context.args) > 1 else "🔔 Recordatorio máster"
        hora_obj = datetime.datetime.strptime(hora, "%H:%M")
        ahora = datetime.datetime.now()
        fecha_obj = ahora.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0)
        if fecha_obj < ahora:
            fecha_obj += datetime.timedelta(days=1)
        scheduler.add_job(enviar_recordatorio_programado, 'date', run_date=fecha_obj, args=[mensaje])
        await update.message.reply_text(f"✅ Recordatorio para {hora}:\n> {mensaje}", parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Usa el formato: /recordar HH:MM mensaje personalizado", parse_mode="Markdown")
#📘 Comando /reglas

async def reglas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = """📘 Reglas del Máster de TV Educativo:

1️⃣ Respeto y disciplina  
2️⃣ Puntualidad 🕒  
3️⃣ Orden técnico y pedagógico  
4️⃣ Cámara lista, mente creativa 🎥  
5️⃣ Voz firme y clara al pueblo venezolano 🇻🇪"""
    await update.message.reply_text(texto, parse_mode="Markdown")
#📊 Comando /llegadas

async def llegadas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media = registro_llegadas.get("media_tarde", 0)
    muy = registro_llegadas.get("muy_tarde", 0)
    await update.message.reply_text(
        f"""📊 Registro de entregas detectadas:

🟡 Media hora tarde: {media} veces 😥  
🔴 Muy tarde: {muy} veces 😩

🕓 ¡La puntualidad habla por ti, operador del Máster!""",
        parse_mode="Markdown"
    )

# 🔋 Comando /estado para confirmar conexión
async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔋 *ColombinoBot está activo y funcionando en Render 24/7* 🇻🇪🎬",
        parse_mode="Markdown"
    )

#🛡️ Detector de entrega de guardia

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
        mensaje = f"🛡️ Guardia recibida — Turno asignado: " + ", ".join(nombres)
        if hora_actual >= datetime.time(10, 31) and hora_actual < datetime.time(11, 0):
            mensaje += "\n🕒 Llegaste media hora tarde 😥 pero aceptable."
            registro_llegadas["media_tarde"] += 1
        elif hora_actual >= datetime.time(11, 0):
            mensaje += "\n🚨 Llegaste MUY pero MUY tarde 😩. No es bueno llegar así…"
            registro_llegadas["muy_tarde"] += 1
        else:
            mensaje += "\n🟢 ¡Guardia dentro del tiempo! ✅ Excelente puntualidad."
        await update.message.reply_text(mensaje, parse_mode="Markdown")
🚀 Activar bot

app. add_handler(Comm andHandler ("estado" estado))
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("recordar", recordar))
app.add_handler(CommandHandler("reglas", reglas))
app.add_handler(CommandHandler("llegadas", llegadas))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detectar_guardia))
app.run_polling() 