import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8990018709:AAERV3m40jVMHvjNkj4BZyRgzzjPIpT4rzo"
ADMIN_ID = 7242000253
ADMIN_USERNAME = "Mohammaddd0f" # آیدی پشتیبانی و ادمین

bot = telebot.TeleBot(TOKEN)
waiting_for_config = {}

# چینش دقیق دکمه‌های پایین صفحه
def main_reply_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # ردیف 1
    btn_buy = KeyboardButton("💳 خرید سرور")
    markup.add(btn_buy)
    
    # ردیف 2
    btn_test = KeyboardButton("🎁 دریافت اکانت تست")
    markup.add(btn_test)
    
    # ردیف 3 (دو تایی کنار هم)
    btn_accounts = KeyboardButton("👤 حساب‌های من")
    btn_help = KeyboardButton("❓ آموزش اتصال")
    markup.add(btn_accounts, btn_help)
    
    # ردیف 4
    btn_partner = KeyboardButton("👥 درخواست همکاری عمده")
    markup.add(btn_partner)
    
    # ردیف 5
    btn_support = KeyboardButton("💬 پشتیبانی")
    markup.add(btn_support)
    
    return markup

# منوی انتخاب تعرفه خرید اشتراک (شیشه‌ای)
def buy_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_1gb = InlineKeyboardButton("💳 اقتصادی - 1 گیگ - 5,000 تومان", callback_data="buy_1gb")
    btn_5gb = InlineKeyboardButton("💳 پیشنهادی - 5 گیگ - 25,000 تومان", callback_data="buy_5gb")
    btn_20gb = InlineKeyboardButton("💳 ویژه - 20 گیگ - 100,000 تومان", callback_data="buy_20gb")
    btn_custom = InlineKeyboardButton("➕ حجم دلخواه (1 تا 1000 گیگ)", callback_data="buy_custom")
    btn_back = InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")
    markup.add(btn_1gb, btn_5gb, btn_20gb, btn_custom, btn_back)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    # متن خوش‌آمدگویی شکیل همراه با پوستر
    caption_text = (
        f"👑 **به ربات اختصاصی تاج وی‌پی‌ان خوش آمدید، {user_name} عزیز!**\n\n"
        "───────────────\n"
        "⚡️ **پادشاهی سرعت، امنیت و آزادی**\n"
        "🇺🇸 سرورهای اختصاصی آمریکا [ مناسب برای اینترنت ملی ]\n"
        "───────────────\n\n"
        "🛡 از منوی زیر برای خرید، دریافت تست یا مدیریت حساب استفاده کنید:"
    )
    
    # لطفا عکس پوستر را به ربات بفرستید و آیدی فایل آن را جایگزین مقدار زیر کنید 
    # (یا می‌توانید عکس را مستقیم آپلود کنید و file_id آن را بگذارید)
    # فعلا متن و ساختار ارسال عکس فعال است:
    try:
        # اگر می‌خواهید عکس با لینک مستقیم یا از طریق ارسال خودکار باشد:
        # پیش‌فرض ساختار ارسال کپشن روی عکس:
        bot.send_message(message.chat.id, caption_text, reply_markup=main_reply_menu(), parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, caption_text, reply_markup=main_reply_menu(), parse_mode="Markdown")

# مدیریت پیام‌های متنی و بررسی حالت انتظار کانفیگ برای ادمین
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text
    
    if message.from_user.id == ADMIN_ID and ADMIN_ID in waiting_for_config:
        target_user_id = waiting_for_config[ADMIN_ID]
        config_text = text
        try:
            bot.send_message(
                target_user_id,
                f"🎉 **پرداخت شما تایید شد و سرویس شما فعال گردید!**\n\n"
                f"🔗 **لینک اشتراک اختصاصی شما:**\n`{config_text}`\n\n"
                "از بخش «آموزش اتصال» می‌توانید نحوه راه‌اندازی را مشاهده کنید.",
                parse_mode="Markdown"
            )
            bot.reply_to(message, "✅ کانفیگ با موفقیت برای کاربر ارسال شد!")
        except Exception as e:
            bot.reply_to(message, "❌ خطا در ارسال کانفیگ به کاربر (ممکن است ربات را بلاک کرده باشد).")
        
        del waiting_for_config[ADMIN_ID]
        return

    # دکمه‌های منوی اصلی
    if text == "💳 خرید سرور":
        msg_text = (
            "💳 **خرید حساب اختصاصی**\n\n"
            "پنل: 🇺🇸 **آمریکا [ مناسب برای اینترنت ملی ]**\n"
            "قیمت فعلی هر گیگ: **5,000 تومان**\n"
            "محدودیت حجم: از 1 تا 1000 گیگ\n\n"
            "یکی از تعرفه‌ها را انتخاب کنید یا مقدار دلخواه بفرستید."
        )
        bot.send_message(chat_id, msg_text, reply_markup=buy_menu(), parse_mode="Markdown")
        
    elif text == "🎁 دریافت اکانت تست":
        bot.send_message(
            chat_id, 
            f"🎁 **دریافت اکانت تست رایگان:**\n\n"
            f"⚠️ هر کاربر عزیز فقط یک‌بار می‌تواند تست دریافت کند.\n\n"
            f"💬 برای دریافت اکانت تست، لطفاً به پیوی پشتیبانی / ادمین مراجعه کنید:\n"
            f"👉 @{ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
        
    elif text == "👤 حساب‌های من":
        bot.send_message(chat_id, "👤 شما در حال حاضر هیچ اشتراک فعالی در این ربات ندارید.")
        
    elif text == "❓ آموزش اتصال":
        bot.send_message(
            chat_id, 
            "❓ **آموزش اتصال به وی‌پی‌ان:**\n\n"
            "• اندروید: اپلیکیشن V2RayNG\n"
            "• آیفون: اپلیکیشن FoXray یا Streisand\n"
            "• ویندوز: اپلیکیشن v2rayN\n\n"
            "لینک اشتراک خود را کپی کرده و داخل برنامه وارد کنید."
        )
        
    elif text == "👥 درخواست همکاری عمده":
        bot.send_message(chat_id, f"👥 برای ثبت درخواست همکاری عمده و دریافت پنل همکار، به ادمین پیام دهید:\n@{ADMIN_USERNAME}")
        
    elif text == "💬 پشتیبانی":
        bot.send_message(chat_id, f"💬 برای ارتباط با پشتیبانی به آیدی زیر پیام دهید:\n@{ADMIN_USERNAME}")

# مدیریت دکمه‌های شیشه‌ای (خرید و پنل ادمین)
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
            bot.send_message(call.message.chat.id, "✍️ لطفاً مقدار حجم مورد نظر خود را به عدد (بین 1 تا 1000 گیگ) در قالب پیام ارسال کنید:")
            return
            
        bot.answer_callback_query(call.id, f"انتخاب پلن {gb} گیگی")
        invoice_text = (
            f"🛒 **فاکتور خرید اشتراک آمریکا**\n\n"
            f"📦 حجم: {gb} گیگابایت\n"
            f"💰 قابل پرداخت: {price} تومان\n\n"
            "───────────────\n"
            "💳 **اطلاعات کارت به کارت:**\n"
            "`6037997328226635`\n"
            "به نام: **محمد فتحی**\n\n"
            "⏳ لطفاً پس از واریز وجه، **تصویر فیش واریزی** خود را همینجا ارسال کنید تا سرویس شما صادر شود."
        )
        bot.send_message(call.message.chat.id, invoice_text, parse_mode="Markdown")
        
    elif call.data == "main_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "منوی اصلی:", reply_markup=main_reply_menu())

    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        data_parts = call.data.split("_")
        action = data_parts[0]
        target_user_id = data_parts[1]
        
        if action == "approve":
            bot.answer_callback_query(call.id, "فیش تایید شد. حالا لینک کانفیگ را بفرستید.")
            waiting_for_config[ADMIN_ID] = target_user_id
            bot.send_message(
                ADMIN_ID, 
                f"✅ فیش کاربر با آیدی `{target_user_id}` تایید شد.\n\n"
                "👇 **اکنون لینک اشتراک (کانفیگ) را همینجا بفرستید تا برای این کاربر ارسال شود:**",
                parse_mode="Markdown"
            )
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\n🟢 **[ وضعیت: فیش تایید شد - در انتظار ارسال کانفیگ ]**",
                parse_mode="Markdown"
            )
        elif action == "reject":
            bot.answer_callback_query(call.id, "فیش رد شد.")
            bot.send_message(target_user_id, "❌ **فیش واریزی شما رد شد.**\n\nلطفاً در صورت داشتن هرگونه سوال با پشتیبانی در ارتباط باشید.")
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\n🔴 **[ وضعیت: فیش رد شد ]**",
                parse_mode="Markdown"
            )

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user = message.from_user
    caption = (
        f"📥 **فیش واریزی جدید!**\n\n"
        f"👤 نام کاربر: {user.first_name}\n"
        f"🆔 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
        f"🔢 آیدی عددی: `{user.id}`"
    )
    
    admin_markup = InlineKeyboardMarkup(row_width=2)
    btn_approve = InlineKeyboardButton(f"✅ تایید ({user.first_name})", callback_data=f"approve_{user.id}")
    btn_reject = InlineKeyboardButton(f"❌ رد ({user.first_name})", callback_data=f"reject_{user.id}")
    admin_markup.add(btn_approve, btn_reject)
    
    try:
        bot.send_photo(
            chat_id=ADMIN_ID, 
            photo=message.photo[-1].file_id, 
            caption=caption, 
            reply_markup=admin_markup, 
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ فیش واریزی شما با موفقیت برای پشتیبانی ارسال شد. پس از بررسی، لینک اشتراک برای شما ارسال خواهد شد.")
    except Exception as e:
        bot.reply_to(message, "❌ خطا در ارسال فیش.")

if __name__ == '__main__':
    print("Taj VPN Bot is running successfully...")
    bot.infinity_polling()
    
