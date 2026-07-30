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

# ⚙️ تنظیمات پنل
PANEL_URL = "https://sub9.kaliteam.ir:8000"
PANEL_USERNAME = "Mohammad1099"
PANEL_PASSWORD = "@MohammadFathi1099"

bot = telebot.TeleBot(TOKEN)
waiting_for_config = {}
user_pending_plan = {}
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

# تابع اصلاح‌شده و دقیق ساخت خودکار کانفیگ با پنل X-UI
def create_vless_config_via_panel(username, gb_amount):
    try:
        session = requests.Session()
        base_url = PANEL_URL.rstrip('/')
        
        # ۱. لاگین به پنل
        login_url = f"{base_url}/login"
        login_data = {
            "username": PANEL_USERNAME,
            "password": PANEL_PASSWORD
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json, text/plain, */*"
        }
        
        login_res = session.post(login_url, data=login_data, headers=headers, verify=False, timeout=15)
        
        try:
            res_json = login_res.json()
            if not res_json.get("success"):
                print("Login failed response json:", res_json)
                return None
        except Exception as err:
            print("Login JSON decode error:", err)
            if login_res.status_code != 200:
                print("Login status code error:", login_res.status_code)
                return None

        # ۲. گرفتن لیست اینباندها
        inbounds_url = f"{base_url}/panel/api/inbounds/list"
        inbounds_res = session.get(inbounds_url, headers=headers, verify=False, timeout=15)
        inbounds_data = inbounds_res.json()
        
        if not inbounds_data.get("success") or not inbounds_data.get("obj"):
            print("Failed to fetch inbounds:", inbounds_data)
            return None
        
        inbounds = inbounds_data["obj"]
        inbound_id = inbounds[0]['id']
        
        client_uuid = str(uuid.uuid4())
        expire_time = int((time.time() + (30 * 86400)) * 1000) # ۳۰ روزه
        total_bytes = int(gb_amount) * 1024 * 1024 * 1024

        # ۳. ساخت کلاینت جدید
        add_url = f"{base_url}/panel/api/inbounds/addClient"
        add_data = {
            "id": inbound_id,
            "settings": f'{{"clients": [{{"id": "{client_uuid}", "alterId": 0, "email": "{username}", "limitIp": 0, "totalGB": {total_bytes}, "expiryTime": {expire_time}, "enable": true, "tgId": "", "subId": ""}}]}}'
        }

        add_res = session.post(add_url, json=add_data, headers=headers, verify=False, timeout=15)
        add_json = add_res.json()
        
        if add_json.get("success"):
            server_ip = base_url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            link = f"vless://{client_uuid}@{server_ip}:443?encryption=none&security=tls&type=tcp&headerType=none#{username}"
            return link
        else:
            print("Add client failed:", add_json)
    except Exception as e:
        print(f"Panel Connection Error: {e}")
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
    
    # دریافت کانفیگ دستی و ارسال به کاربر
    if message.from_user.id == ADMIN_ID and ADMIN_ID in waiting_for_config:
        data = waiting_for_config[ADMIN_ID]
        target_user_id = data["user_id"]
        
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
    user_id = call.from_user.id
    
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
            
        user_pending_plan[user_id] = gb

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

    elif call.data.startswith("auto_approve_"):
        _, _, target_user_id, gb_val = call.data.split("_")
        bot.answer_callback_query(call.id, "در حال ساخت خودکار اکانت در پنل...")
        
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
                bot.send_message(ADMIN_ID, f"✅ اکانت خودکار ساخته شد و برای کاربر ارسال گردید:\n`{config_link}`", parse_mode="Markdown")
            except Exception:
                bot.send_message(ADMIN_ID, "❌ خطا در ارسال پیام به کاربر.")
        else:
            bot.send_message(ADMIN_ID, "❌ خطا در ارتباط با پنل! لطفاً از دکمه ارسال دستی استفاده کنید.")

    elif call.data.startswith("manual_approve_"):
        _, _, target_user_id = call.data.split("_")
        bot.answer_callback_query(call.id, "لطفاً کانفیگ دستی را ارسال کنید.")
        waiting_for_config[ADMIN_ID] = {"user_id": int(target_user_id)}
        bot.send_message(ADMIN_ID, f"✍️ لطفاً لینک کانفیگ دستی را برای کاربر (ID: `{target_user_id}`) بفرستید:", parse_mode="Markdown")

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
    gb_val = user_pending_plan.get(user.id, 5)
    
    caption = f"📥 **فیش واریزی جدید!**\n\n👤 نام: {user.first_name}\n🆔 آیدی: `{user.id}`\n📦 حجم درخواستی: {gb_val} گیگ"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🤖 ارسال خودکار از پنل", callback_data=f"auto_approve_{user.id}_{gb_val}"),
        InlineKeyboardButton("✍️ ارسال دستی کانفیگ", callback_data=f"manual_approve_{user.id}")
    )
    markup.add(
        InlineKeyboardButton("❌ رد فیش", callback_data=f"reject_{user.id}")
    )
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    bot.reply_to(message, "✅ فیش شما ارسال شد و به زودی بررسی می‌گردد.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True, interval=2)
            
