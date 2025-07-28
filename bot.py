from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# 🔑 Reemplaza con tu token real
TOKEN = "8238726820:AAGU_CouD4wXuxMDMjloF76NiC3LjsPdwRY"

# Variable para almacenar el chat donde enviar mensajes automáticos
CHAT_ID_GLOBAL = None

# ⏱️ Iniciar el programador de tareas
scheduler = BackgroundScheduler()
scheduler.start()

# 🕘 Enviar mensaje automático diario
def enviar_mensaje_diario():
    if CHAT_ID_GLOBAL:
        app.bot.send_message(chat_id=CHAT_ID_GLOBAL, text="☀️ ¡Buenos días! Este es tu recordatorio diario.")

# Programar mensaje diario a las 09:00
scheduler.add_job(enviar_mensaje_diario, 'cron', hour=9, minute=0)

# 📲 Comando /start con botones
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID_GLOBAL
    CHAT_ID_GLOBAL = update.effective_chat.id

    teclado = [
        [InlineKeyboardButton("⏰ Programar recordatorio", callback_data='recordar')],
        [InlineKeyboardButton("📋 Ver ayuda", callback_data='ayuda')]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text("¡Hola, soy *ColombinoMbot* 🦜! ¿Qué deseas hacer?", reply_markup=reply_markup)

# 🖱️ Respuesta cuando se pulsa un botón
async def boton_pulsado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'recordar':
        await query.edit_message_text("Usa el comando:\n/recordar HH:MM Tu mensaje")
    elif query.data == 'ayuda':
        await query.edit_message_text("Comandos:\n/start → Menú\n/recordar HH:MM texto")

# ⏰ Comando para programar recordatorio personalizado
async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hora = context.args[0]
        mensaje = ' '.join(context.args[1:]) if len(context.args) > 1 else "¡Recordatorio!"
        hora_obj = datetime.datetime.strptime(hora, "%H:%M")
        ahora = datetime.datetime.now()
        fecha_obj = ahora.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0)

        if fecha_obj < ahora:
            fecha_obj += datetime.timedelta(days=1)

        scheduler.add_job(
            enviar_recordatorio,
            'date',
            run_date=fecha_obj,
            args=[context, update.effective_chat.id, mensaje]
        )

        await update.message.reply_text(f"✅ Programado para las {hora}: \"{mensaje}\"")
    except:
        await update.message.reply_text("❌ Formato incorrecto.\nUsa: /recordar HH:MM Tu mensaje")

# 📤 Enviar recordatorio cuando se cumple la hora
async def enviar_recordatorio(context, chat_id, mensaje):
    await context.bot.send_message(chat_id=chat_id, text=f"🔔 Recordatorio: {mensaje}")

# 🚀 Iniciar el bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("recordar", recordar))
app.add_handler(CallbackQueryHandler(boton_pulsado))

print("✅ ColombinoMbot está corriendo...")
app.run_polling()
