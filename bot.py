import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "7481829667:AAFm2BA6GQA79RVDtbCh9YrLcRUsyJKCHCQ"
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا! أرسل لي وصفًا وسأقوم بإنشاء صورة ذكاء صناعي لك."
    )

def generate_image_from_hf(prompt):
    response = requests.post(
        HF_API_URL,
        json={"inputs": prompt}
    )
    if response.status_code == 200:
        return response.content
    else:
        return None

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ جاري إنشاء الصورة... انتظر 20-40 ثانية.")
    image_data = generate_image_from_hf(prompt)
    if image_data:
        await update.message.reply_photo(image_data)
    else:
        await update.message.reply_text("❌ حدث خطأ، حاول لاحقًا.")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

print("✅ Bot is running...")
app.run_polling()
