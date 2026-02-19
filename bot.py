import os
import io
import wikipedia
import requests
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")

# -------- START MENU --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Text to PDF", callback_data="text_pdf")],
        [InlineKeyboardButton("📂 PDF to Text", callback_data="pdf_text")],
        [InlineKeyboardButton("🌍 Translate to English", callback_data="translate")],
        [InlineKeyboardButton("🧠 Ask Question", callback_data="ask")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 Welcome to BrainForge Bot\n\nSelect an option:",
        reply_markup=reply_markup,
    )


# -------- BUTTON HANDLER --------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["mode"] = query.data

    if query.data == "text_pdf":
        await query.message.reply_text("Send the text you want to convert into PDF.")
    elif query.data == "pdf_text":
        await query.message.reply_text("Send the PDF file.")
    elif query.data == "translate":
        await query.message.reply_text("Send text to translate into English.")
    elif query.data == "ask":
        await query.message.reply_text("Ask your question.")


# -------- MESSAGE HANDLER --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    # TEXT TO PDF
    if mode == "text_pdf" and update.message.text:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph(update.message.text, styles["Normal"])]
        doc.build(story)
        buffer.seek(0)

        await update.message.reply_document(
            document=buffer, filename="BrainForge.pdf"
        )

    # PDF TO TEXT
    elif mode == "pdf_text" and update.message.document:
        file = await update.message.document.get_file()
        pdf_bytes = await file.download_as_bytearray()
        reader = PdfReader(io.BytesIO(pdf_bytes))

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if text:
            await update.message.reply_text(text[:4000])
        else:
            await update.message.reply_text("Could not extract text.")

    # TRANSLATE
    elif mode == "translate" and update.message.text:
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {"q": update.message.text, "langpair": "auto|en"}
            response = requests.get(url, params=params).json()
            translated = response["responseData"]["translatedText"]
            await update.message.reply_text(f"Translated:\n{translated}")
        except:
            await update.message.reply_text("Translation failed.")

    # ASK QUESTION
    elif mode == "ask" and update.message.text:
        try:
            summary = wikipedia.summary(update.message.text, sentences=3)
            await update.message.reply_text(summary)
        except:
            await update.message.reply_text("No answer found.")

    else:
        await update.message.reply_text("Type /start to choose option.")


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
