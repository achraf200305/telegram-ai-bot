import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# توكن البوت
BOT_TOKEN = "7481829667:AAFm2BA6GQA79RVDtbCh9YrLcRUsyJKCHCQ"

# رابط الإعلان الخاص بك
AD_LINK = "https://shrinkme.ink/ADSboot"

# رابط الدفع بايبال
PAYPAL_LINK = "https://www.paypal.me/achrafkadi/7"

# بريد خدمة العملاء
SUPPORT_EMAIL = "achraf.kadi2003@gmail.com"

# تخزين بيانات المستخدمين
user_data = {}

# الحدود المجانية
FREE_IMAGES = 3
FREE_ANIME = 3
FREE_QUESTIONS = 20

# تفعيل اللوج
logging.basicConfig(level=logging.INFO)

# بدء البوت
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
        "اكتب طلبك الآن!"
    )

# فحص الرصيد
def has_balance(user_id):
    data = user_data.get(user_id, {})
    return (data.get("images",0) > 0 or 
            data.get("anime",0) > 0 or 
            data.get("questions",0) > 0)

# تقليل الرصيد
def reduce_balance(user_id, task_type):
    if user_id not in user_data:
        return False
    if user_data[user_id][task_type] > 0:
        user_data[user_id][task_type] -= 1
        return True
    return False

# إرسال خيارات الدفع أو الإعلان
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

# التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not has_balance(user_id):
        await send_payment_or_ads(update, context)
        return
    
    text = update.message.text.lower()
    
    if "انمي" in text:
        if reduce_balance(user_id, "anime"):
            await update.message.reply_text("✅ تم تحويل الصورة إلى أنمي (مثال تجريبي).")
        else:
            await send_payment_or_ads(update, context)
    elif "صورة" in text:
        if reduce_balance(user_id, "images"):
            await update.message.reply_text("✅ تم إنشاء الصورة (مثال تجريبي).")
        else:
            await send_payment_or_ads(update, context)
    else:
        if reduce_balance(user_id, "questions"):
            await update.message.reply_text("✅ هذا رد مثال على سؤالك.")
        else:
            await send_payment_or_ads(update, context)

# التعامل مع الأزرار
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

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
    
