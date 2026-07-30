import telebot
import time
import requests
import urllib3
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "8990018709:AAH8_Ix5jPnMhPw81vjqJJXeNYIT6Ovd2vI"
ADMIN_ID = 7242000253
ADMIN_USERNAME = "Mohammaddd0f"

# ⚙️ اطلاعات پنل پاسارگاد شما
PANEL_URL = "https://pasarguard-production-6f62.up.railway.app/"
PANEL_USERNAME = "admin"
PANEL_PASSWORD = "PaSarGuard2026!"

bot = telebot.TeleBot(TOKEN)
waiting_for_config = {}
processed_messages = {}

def is_duplicate(message_id):
    current_time = time.time()
    if message_id in processed_messages:
        if current_time - processed_messages[message_id] < 3:
            return True
    processed_messages[message_id] = current_time
    keys_to_del = [k for k, v in processed_messages.items() if current_time - v > 10]
    for k in keys_to_del:
        del processed_messages[k]
    return False

# تابع کامل و اصلاح‌شده برای اتصال و ساخت خودکار کلاینت در پنل X-UI
def create_vless_config_via_panel(username, gb_amount):
    try:
        session = requests.Session()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        # ۱. لاگین به پنل
        login_res = session.post(
            f"{PANEL_URL}login", 
            json={"username": PANEL_USERNAME, "password": PANEL_PASSWORD}, 
            headers=headers, 
            verify=False
        )
        
        if not login_res.json().get("success"):
            print("Login failed:", login_res.text)
            return None

        # ۲. گرفتن لیست اینباندها
        inbounds_res = session.get(f"{PANEL_URL}panel/api/inbounds/list", headers=headers, verify=False)
        inbounds_data = inbounds_res.json()
        
        if not inbounds_data.get("success") or not inbounds_data.get("obj"):
            print("Failed to get inbounds")
            return None
        
        inbounds = inbounds_data["obj"]
        inbound_id = inbounds[0]['id']
        
        client_uuid = str(uuid.uuid4())
        expire_time = int((time.time() + (30 * 86400)) * 1000) # 30 روزه
        total_bytes = int(gb_amount) * 1024 * 1024 * 1024

        # ۳. ساخت کلاینت جدید
        add_data = {
            "id": inbound_id,
            "settings": f'{{"clients": [{{"id": "{client_uuid}", "alterId": 0, "email": "{username}", "limitIp": 0, "totalGB": {total_bytes}, "expiryTime": {expire_time}, "enable": true, "tgId": "", "subId": ""}}]}}'
        }

        add_res = session.post(f"{PANEL_URL}panel/api/inbounds/addClient", json=add_data, headers=headers, verify=False)
        res_json = add_res.json()
        
        if res_json.get("success"):
            server_ip = PANEL_URL.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            link = f"vless://{client_uuid}@{server_ip}:443?encryption=none&security=tls&type=tcp&headerType=none#{username}"
            return link
        else:
            print("Add client failed:", res_json)
    except Exception as e:
        print(f"Panel Error: {e}")
    return None

def main_inline_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 خرید سرور اختصاصی", callback_data="menu_buy"),
        InlineKeyboardButton("🎁 دریافت اکانت تست", callback_data="menu_test")
    )
    markup.add(
        InlineKeyboardButton("👤 حساب‌های من", callback_data="menu_account"),
        InlineKeyboardButton("❓ آموزش اتصال", callback_data="menu_help")
    )
    markup.add(
        InlineKeyboardButton("👥 درخواست همکاری عمده", callback_data="menu_partner")
    )
    markup.add(
        InlineKeyboardButton("💬 ارتباط با پشتیبانی", callback_data="menu_support")
    )
    return markup

def buy_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 اقتصادی - 1 گیگ - 5,000 تومان", callback_data="buy_1gb"),
        InlineKeyboardButton("💳 پیشنهادی - 5 گیگ - 25,000 تومان", callback_data="buy_5gb"),
        InlineKeyboardButton("💳 ویژه - 20 گیگ - 100,000 تومان", callback_data="buy_20gb"),
        InlineKeyboardButton("➕ حجم دلخواه", callback_data="buy_custom"),
        InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_duplicate(message.message_id):
        return
    user_name = message.from_user.first_name
    caption_text = (
        f"👑 **به ربات اختصاصی تاج وی‌پی‌ان خوش آمدید، {user_name} عزیز!**\n\n"
        "───────────────\n"
        "⚡️ **پادشاهی سرعت، امنیت و آزادی**\n"
        "🇺🇸 سرورهای اختصاصی آمریکا [ مناسب برای اینترنت ملی ]\n"
        "───────────────\n\n"
        "🛡 از منوی شیشه‌ای زیر برای خرید، دریافت تست یا مدیریت حساب استفاده کنید:"
    )
    try:
        with open('poster.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=main_inline_menu(), parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=main_inline_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if is_duplicate(message.message_id):
        return
    chat_id = message.chat.id
    text = message.text
    
    if message.from_user.id == ADMIN_ID and ADMIN_ID in waiting_for_config:
        data = waiting_for_config[ADMIN_ID]
        target_user_id = data["user_id"]
        mode = data["mode"]
        
        if mode == "manual":
            try:
                bot.send_message(
                    target_user_id,
                    f"🎉 **پرداخت شما تایید شد و سرویس شما فعال گردید!**\n\n"
                    f"🔗 **لینک اشتراک اختصاصی شما:**\n`{text}`\n\n"
                    "از بخش «آموزش اتصال» می‌توانید نحوه راه‌اندازی را مشاهده کنید.",
                    parse_mode="Markdown"
                )
                bot.reply_to(message, "✅ کانفیگ دستی با موفقیت برای کاربر ارسال شد!")
            except Exception:
                bot.reply_to(message, "❌ خطا در ارسال کانفیگ.")
        del waiting_for_config[ADMIN_ID]
        return

    if text:
        bot.send_message(chat_id, "منوی مدیریت و خرید:", reply_markup=main_inline_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "menu_buy":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💳 **خرید حساب اختصاصی**\n\nپنل: 🇺🇸 **آمریکا [ مناسب برای اینترنت ملی ]**\nقیمت هر گیگ: **5,000 تومان**", reply_markup=buy_menu(), parse_mode="Markdown")
    
    elif call.data == "menu_test":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"🎁 برای دریافت اکانت تست به ادمین پیام دهید:\n👉 @{ADMIN_USERNAME}", parse_mode="Markdown")
        
    elif call.data == "menu_account":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "👤 شما در حال حاضر هیچ اشتراک فعالی ندارید.")
        
    elif call.data == "menu_help":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "❓ آموزش اتصال:\n• اندروید: V2RayNG\n• آیفون: FoXray\n• ویندوز: v2rayN")
        
    elif call.data == "menu_partner":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"👥 برای همکاری عمده به ادمین پیام دهید:\n@{ADMIN_USERNAME}")
        
    elif call.data == "menu_support":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"💬 پشتیبانی:\n@{ADMIN_USERNAME}")

    elif call.data.startswith("buy_"):
        plan = call.data.split("_")[1]
        if plan == "1gb":
            gb, price = 1, "5,000"
        elif plan == "5gb":
            gb, price = 5, "25,000"
        elif plan == "20gb":
            gb, price = 20, "100,000"
        elif plan == "custom":
            bot.answer_callback_query(call.id, "حجم دلخواه")
            bot.send_message(chat_id, "✍️ مقدار حجم دلخواه خود را به عدد بفرستید:")
            return
            
        bot.answer_callback_query(call.id, f"پلن {gb} گیگی")
        invoice_text = (
            f"🛒 **فاکتور خرید اشتراک آمریکا**\n\n📦 حجم: {gb} گیگ\n💰 قابل پرداخت: {price} تومان\n\n"
            "───────────────\n💳 **کارت به کارت:**\n`6037997328226635`\nبه نام: **محمد فتحی**\n\n"
            "⏳ پس از واریز، **فیش واریزی** را همینجا بفرستید."
        )
        bot.send_message(chat_id, invoice_text, parse_mode="Markdown")
        
    elif call.data == "main_menu":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(chat_id, "منوی اصلی:", reply_markup=main_inline_menu())

    elif call.data.startswith("approve_"):
        _, target_user_id, gb_val = call.data.split("_")
        bot.answer_callback_query(call.id, "انتخاب نحوه ارسال...")
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🤖 ساخت و ارسال خودکار", callback_data=f"auto_{target_user_id}_{gb_val}"),
            InlineKeyboardButton("✍️ ارسال دستی لینک", callback_data=f"manual_{target_user_id}")
        )
        bot.send_message(ADMIN_ID, f"⚡️ نحوه ارسال کانفیگ برای کاربر `{target_user_id}` را انتخاب کنید:", reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("auto_"):
        _, target_user_id, gb_val = call.data.split("_")
        bot.answer_callback_query(call.id, "در حال ساخت اکانت در پنل پاسارگاد...")
        
        config_link = create_vless_config_via_panel(f"user_{target_user_id}", gb_val)
        
        if config_link:
            try:
                bot.send_message(
                    int(target_user_id),
                    f"🎉 **پرداخت شما تایید شد و سرویس شما خودکار فعال گردید!**\n\n"
                    f"🔗 **لینک اشتراک اختصاصی شما:**\n`{config_link}`\n\n"
                    "از بخش «آموزش اتصال» می‌توانید نحوه راه‌اندازی را مشاهده کنید.",
                    parse_mode="Markdown"
                )
                bot.send_message(ADMIN_ID, f"✅ اکانت با موفقیت ساخته شد و برای کاربر ارسال گردید:\n`{config_link}`", parse_mode="Markdown")
            except Exception:
                bot.send_message(ADMIN_ID, "❌ خطا در ارسال پیام به کاربر.")
        else:
            bot.send_message(ADMIN_ID, "❌ خطا در ارتباط با پنل پاسارگاد! لطفاً بررسی کنید.")

    elif call.data.startswith("manual_"):
        _, target_user_id = call.data.split("_")
        bot.answer_callback_query(call.id)
        waiting_for_config[ADMIN_ID] = {"user_id": int(target_user_id), "mode": "manual"}
        bot.send_message(ADMIN_ID, "✍️ لینک کانفیگ دستی را بفرستید تا برای کاربر ارسال شود:", parse_mode="Markdown")

    elif call.data.startswith("reject_"):
        _, target_user_id = call.data.split("_")
        bot.answer_callback_query(call.id, "رد شد.")
        try:
            bot.send_message(int(target_user_id), "❌ فیش واریزی شما توسط ادمین رد شد.")
        except Exception:
            pass
        bot.send_message(ADMIN_ID, "❌ فیش مورد نظر رد شد.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    if is_duplicate(message.message_id):
        return
    user = message.from_user
    gb_val = 5 
    
    caption = f"📥 **فیش واریزی جدید!**\n\n👤 نام: {user.first_name}\n🆔 آیدی: `{user.id}`"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ تایید و ارسال", callback_data=f"approve_{user.id}_{gb_val}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    bot.reply_to(message, "✅ فیش شما ارسال شد و به زودی بررسی می‌گردد.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True, interval=2)
        
