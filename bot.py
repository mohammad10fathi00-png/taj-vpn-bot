import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8990018709:AAH8_Ix5jPnMhPw81vjqJJXeNYIT6Ovd2vI"
ADMIN_ID = 7242000253
ADMIN_USERNAME = "Mohammaddd0f"

bot = telebot.TeleBot(TOKEN)
waiting_for_config = {}

def main_reply_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💳 خرید سرور"))
    markup.add(KeyboardButton("🎁 دریافت اکانت تست"))
    markup.add(KeyboardButton("👤 حساب‌های من"), KeyboardButton("❓ آموزش اتصال"))
    markup.add(KeyboardButton("👥 درخواست همکاری عمده"))
    markup.add(KeyboardButton("💬 پشتیبانی"))
    return markup

def buy_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 اقتصادی - 1 گیگ - 5,000 تومان", callback_data="buy_1gb"),
        InlineKeyboardButton("💳 پیشنهادی - 5 گیگ - 25,000 تومان", callback_data="buy_5gb"),
        InlineKeyboardButton("💳 ویژه - 20 گیگ - 100,000 تومان", callback_data="buy_20gb"),
        InlineKeyboardButton("➕ حجم دلخواه (1 تا 1000 گیگ)", callback_data="buy_custom"),
        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    caption_text = (
        f"👑 **به ربات اختصاصی تاج وی‌پی‌ان خوش آمدید، {user_name} عزیز!**\n\n"
        "───────────────\n"
        "⚡️ **پادشاهی سرعت، امنیت و آزادی**\n"
        "🇺🇸 سرورهای اختصاصی آمریکا [ مناسب برای اینترنت ملی ]\n"
        "───────────────\n\n"
        "🛡 از منوی زیر برای خرید، دریافت تست یا مدیریت حساب استفاده کنید:"
    )
    
    try:
        with open('poster.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=main_reply_menu(), parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=main_reply_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text
    
    if message.from_user.id == ADMIN_ID and ADMIN_ID in waiting_for_config:
        target_user_id = waiting_for_config[ADMIN_ID]
        try:
            bot.send_message(
                target_user_id,
                f"🎉 **پرداخت شما تایید شد و سرویس شما فعال گردید!**\n\n"
                f"🔗 **لینک اشتراک اختصاصی شما:**\n`{text}`\n\n"
                "از بخش «آموزش اتصال» می‌توانید نحوه راه‌اندازی را مشاهده کنید.",
                parse_mode="Markdown"
            )
            bot.reply_to(message, "✅ کانفیگ با موفقیت برای کاربر ارسال شد!")
        except Exception:
            bot.reply_to(message, "❌ خطا در ارسال کانفیگ به کاربر.")
        del waiting_for_config[ADMIN_ID]
        return

    if text == "💳 خرید سرور":
        bot.send_message(
            chat_id, 
            "💳 **خرید حساب اختصاصی**\n\nپنل: 🇺🇸 **آمریکا [ مناسب برای اینترنت ملی ]**\nقیمت هر گیگ: **5,000 تومان**", 
            reply_markup=buy_menu(), 
            parse_mode="Markdown"
        )
    elif text == "🎁 دریافت اکانت تست":
        bot.send_message(chat_id, f"🎁 برای دریافت اکانت تست به ادمین پیام دهید:\n👉 @{ADMIN_USERNAME}", parse_mode="Markdown")
    elif text == "👤 حساب‌های من":
        bot.send_message(chat_id, "👤 شما در حال حاضر هیچ اشتراک فعالی ندارید.")
    elif text == "❓ آموزش اتصال":
        bot.send_message(chat_id, "❓ آموزش اتصال:\n• اندروید: V2RayNG\n• آیفون: FoXray\n• ویندوز: v2rayN")
    elif text == "👥 درخواست همکاری عمده":
        bot.send_message(chat_id, f"👥 برای همکاری عمده به ادمین پیام دهید:\n@{ADMIN_USERNAME}")
    elif text == "💬 پشتیبانی":
        bot.send_message(chat_id, f"💬 پشتیبانی:\n@{ADMIN_USERNAME}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("buy_"):
        plan = call.data.split("_")[1]
        if plan == "1gb":
            gb, price = 1, "5,000"
        elif plan == "5gb":
            gb, price = 5, "25,000"
        elif plan == "20gb":
            gb, price = 20, "100,000"
        elif plan == "custom":
            bot.answer_callback_query(call.id, "حجم دلخواه")
            bot.send_message(call.message.chat.id, "✍️ مقدار حجم دلخواه خود را به عدد بفرستید:")
            return
            
        bot.answer_callback_query(call.id, f"پلن {gb} گیگی")
        invoice_text = (
            f"🛒 **فاکتور خرید اشتراک آمریکا**\n\n📦 حجم: {gb} گیگ\n💰 قابل پرداخت: {price} تومان\n\n"
            "───────────────\n💳 **کارت به کارت:**\n`6037997328226635`\nبه نام: **محمد فتحی**\n\n"
            "⏳ پس از واریز، **فیش واریزی** را همینجا بفرستید."
        )
        bot.send_message(call.message.chat.id, invoice_text, parse_mode="Markdown")
        
    elif call.data == "main_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "منوی اصلی:", reply_markup=main_reply_menu())

    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        action, target_user_id = call.data.split("_")
        if action == "approve":
            bot.answer_callback_query(call.id, "تایید شد.")
            waiting_for_config[ADMIN_ID] = target_user_id
            bot.send_message(ADMIN_ID, "✅ لینک کانفیگ را بفرستید:", parse_mode="Markdown")
        elif action == "reject":
            bot.answer_callback_query(call.id, "رد شد.")
            bot.send_message(target_user_id, "❌ فیش واریزی شما رد شد.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user = message.from_user
    caption = f"📥 **فیش واریزی جدید!**\n\n👤 نام: {user.first_name}\n🆔 آیدی: `{user.id}`"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    bot.reply_to(message, "✅ فیش شما ارسال شد.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
