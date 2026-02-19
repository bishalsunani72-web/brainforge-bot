import os
import io
import wikipedia
from googletrans import Translator
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

TOKEN = os.getenv("TOKEN")

translator = Translator()

# -------- START MENU --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Text to PDF", callback_data="text_pdf")],
        [InlineKeyboardButton("📂 PDF to Text", callback_data="pdf_text")],
        [InlineKeyboardButton("🌍 Translate", callback_data="translate")],
        [InlineKeyboardButton("🧠 Ask Question", callback_data="ask")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 Welcome to BrainForge Bot\n\nSelect an option:",
        reply_markup=reply_markup
    )

# -------- BUTTON HANDLER --------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data["mode"] = choice

    if choice == "text_pdf":
        await query.message.reply_text("Send the text you want to convert into PDF.")
    elif choice == "pdf_text":
        await query.message.reply_text("Send the PDF file.")
    elif choice == "translate":
        await query.message.reply_text("Send text to translate.")
    elif choice == "ask":
        await query.message.reply_text("Ask your question.")

# -------- MESSAGE HANDLER --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    if mode == "text_pdf":
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph(update.message.text, styles["Normal"])]
        doc.build(story)
        buffer.seek(0)

        await update.message.reply_document(document=buffer, filename="BrainForge.pdf")

    elif mode == "pdf_text":
        if update.message.document:
            file = await update.message.document.get_file()
            pdf_bytes = await file.download_as_bytearray()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            await update.message.reply_text(text[:4000])

    elif mode == "translate":
        translated = translator.translate(update.message.text, dest="en")
        await update.message.reply_text(f"Translated:\n{translated.text}")

    elif mode == "ask":
        try:
            summary = wikipedia.summary(update.message.text, sentences=3)
            await update.message.reply_text(summary)
        except:
            await update.message.reply_text("Sorry, no answer found.")

# -------- MAIN --------
if TOKEN:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.PDF, handle_message))

    print("BrainForge Bot is running...")
    app.run_polling()
else:
    print("TOKEN not found.")
