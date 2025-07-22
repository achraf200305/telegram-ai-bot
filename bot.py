import logging
import os
import requests
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ✅ توكن البوت
BOT_TOKEN = "7481829667:AAFm2BA6GQA79RVDtbCh9YrLcRUsyJKCHCQ"

# ✅ رابط الإعلان الخاص بك
AD_LINK = "https://shrinkme.ink/ADSboot"

# ✅ رابط الدفع بايبال
PAYPAL_LINK = "https://www.paypal.me/achrafkadi/7"

# ✅ بريد خدمة العملاء
SUPPORT_EMAIL = "achraf.kadi2003@gmail.com"

# ✅ مفتاح Hugging Face سيتم قراءته من Environment Variable
HF_TOKEN = os.getenv("HF_TOKEN")

# ✅ روابط النماذج
STABLE_DIFFUSION_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
ANIME_DIFFUSION_URL = "https://api-inference.huggingface.co/models/hakurei/waifu-diffusion"

# ✅ تخزين بيانات المستخدمين
user_data = {}

# ✅ الحدود المجانية
FREE_IMAGES = 3
FREE_ANIME = 3
FREE_QUESTIONS = 20

logging.basicConfig(level=logging.INFO)

# ✅ طلب صورة من Hugging Face
def generate_image_from_hf(prompt, anime=False):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    url = ANIME_DIFFUSION_URL if anime else STABLE_DIFFUSION_URL
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

# ✅ بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {
        "images": FREE_IMAGES,
        "anime": FREE_ANIME,
        "questions": FREE_QUESTIONS
    }
    await update.message.reply_text(
        "👋 مرحبًا! أنا بوت الصور والذكاء الاصطناعي.\n\n"
        f"🎨 لديك {FREE_IMAGES} صور مجانية\n"
        f"✨ لديك {FREE_ANIME} تحويلات أنمي\n"
        f"❓ لديك {FREE_QUESTIONS} سؤال مجاني\n\n"
        "اكتب:\n"
        "- (صورة + وصفك) لإنشاء صورة\n"
        "- (أنمي + وصفك) لتحويل لأنمي\n"
        "- أو أي سؤال تريده للإجابة"
    )

def has_balance(user_id):
    data = user_data.get(user_id, {})
    return (data.get("images",0) > 0 or 
            data.get("anime",0) > 0 or 
            data.get("questions",0) > 0)

def reduce_balance(user_id, task_type):
    if user_id not in user_data:
        return False
    if user_data[user_id][task_type] > 0:
        user_data[user_id][task_type] -= 1
        return True
    return False

async def send_payment_or_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 الدفع 7$ لشهرين", url=PAYPAL_LINK)],
        [InlineKeyboardButton("🎥 مشاهدة إعلان وتجديد الرصيد", callback_data="watch_ad")],
        [InlineKeyboardButton("🆘 خدمة العملاء", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚠️ انتهى رصيدك!\n\n"
        "يمكنك:\n"
        "✅ الدفع 7$ لشهرين بدون حدود\n"
        "✅ أو مشاهدة إعلان لتجديد رصيدك مجانًا\n"
        "✅ أو التواصل مع خدمة العملاء",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    if not has_balance(user_id):
        await send_payment_or_ads(update, context)
        return
    
    # ✅ طلب صورة عادية
    if text.startswith("صورة") or text.startswith("ارسم"):
        if reduce_balance(user_id, "images"):
            prompt = text.replace("صورة", "").replace("ارسم", "").strip()
            await update.message.reply_text("⏳ جاري إنشاء الصورة، يرجى الانتظار...")
            img = generate_image_from_hf(prompt, anime=False)
            if img:
                await update.message.reply_photo(photo=img, caption="✅ تم إنشاء الصورة!")
            else:
                await update.message.reply_text("❌ حدث خطأ أثناء إنشاء الصورة.")
        else:
            await send_payment_or_ads(update, context)
    
    # ✅ طلب أنمي
    elif text.startswith("انمي") or text.startswith("حوّل"):
        if reduce_balance(user_id, "anime"):
            prompt = text.replace("انمي", "").replace("حوّل", "").strip()
            await update.message.reply_text("⏳ جاري تحويل الصورة إلى أسلوب أنمي...")
            img = generate_image_from_hf(prompt, anime=True)
            if img:
                await update.message.reply_photo(photo=img, caption="✅ تم تحويلها إلى أنمي!")
            else:
                await update.message.reply_text("❌ حدث خطأ أثناء التحويل.")
        else:
            await send_payment_or_ads(update, context)
    
    # ✅ سؤال نصي
    else:
        if reduce_balance(user_id, "questions"):
            await update.message.reply_text("✅ هذا رد تجريبي على سؤالك.")
        else:
            await send_payment_or_ads(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "watch_ad":
        user_data[user_id] = {
            "images": FREE_IMAGES,
            "anime": FREE_ANIME,
            "questions": FREE_QUESTIONS
        }
        await query.message.reply_text(
            "✅ تم تجديد رصيدك مجانًا!\n"
            f"🎨 {FREE_IMAGES} صور\n"
            f"✨ {FREE_ANIME} تحويلات أنمي\n"
            f"❓ {FREE_QUESTIONS} سؤال\n\n"
            f"🎥 شاهد الإعلان لدعمي: {AD_LINK}"
        )
    
    elif query.data == "support":
        await query.message.reply_text(
            f"📩 إذا واجهتك أي مشكلة يمكنك التواصل معنا عبر البريد:\n{SUPPORT_EMAIL}"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
                              
