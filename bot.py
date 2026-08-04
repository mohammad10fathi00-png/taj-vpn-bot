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

PANEL_URL = "https://sub9.kaliteam.ir:8000"
PANEL_USERNAME = "Mohammad1099"
PANEL_PASSWORD = "@MohammadFathi1099"

bot = telebot.TeleBot(TOKEN)
waiting_for_config = {}
waiting_for_custom_gb = {}
user_custom_gb_cache = {}
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

def create_vless_config_via_panel(username, gb_amount):
    try:
        session = requests.Session()
        base_url = PANEL_URL.rstrip('/')
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{base_url}/",
            "Origin": base_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        login_url = f"{base_url}/login"
        payload = {"username": PANEL_USERNAME, "password": PANEL_PASSWORD}
        res = session.post(login_url, json=payload, headers=headers, verify=False, timeout=15)
        
        logged_in = False
        try:
            res_json = res.json()
            if res_json.get("success") is True or res.status_code == 200:
                logged_in = True
        except:
            if res.status_code == 200:
                logged_in = True

        if not logged_in and not session.cookies:
            print("Panel Login Failed.")
            return None

        inbounds_url = f"{base_url}/panel/api/inbounds/list"
        inbounds_res = session.get(inbounds_url, headers=headers, verify=False, timeout=15)
        inbounds_data = inbounds_res.json()
        
        if not inbounds_data.get("success") or not inbounds_data.get("obj"):
            print("Get Inbounds Failed.")
            return None
        
        inbound_id = inbounds_data["obj"][0]['id']
        client_uuid = str(uuid.uuid4())
        expire_time = int((time.time() + (30 * 86400)) * 1000)
        total_bytes = int(gb_amount) * 1024 * 1024 * 1024

        add_url = f"{base_url}/panel/api/inbounds/addClient"
        client_data = {
            "id": inbound_id,
            "settings": f'{{"clients": [{{"id": "{client_uuid}", "alterId": 0, "email": "{username}", "limitIp": 0, "totalGB": {total_bytes}, "expiryTime": {expire_time}, "enable": true, "tgId": "", "subId": ""}}]}}'
        }

        add_res = session.post(add_url, json=client_data, headers=headers, verify=False, timeout=15)
        add_json = add_res.json()
        
        if add_json.get("success"):
            server_ip = base_url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            link = f"vless://{client_uuid}@{server_ip}:443?encryption=none&security=tls&type=tcp&headerType=none#{username}"
            return link
        else:
            print(f"Panel Error Response: {add_json}")
            return None
            
    except Exception as e:
        print(f"Exception in panel connection: {e}")
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
        "⚡️ **پادشاهی سرعت، امنیت و آزادی بی‌حدومرز**\n"
        "🚀 مجهز به سرورهای پرسرعت، پایدار و بدون قطعی\n"
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
    user_id = message.from_user.id
    text = message.text
    
    if user_id in waiting_for_custom_gb:
        del waiting_for_custom_gb[user_id]
        try:
            gb = int(text.strip())
            if gb <= 0:
                raise ValueError()
            price = gb * 5000
            price_formatted = f"{price:,}"
            
            invoice_text = (
                f"🛒 **فاکتور خرید اشتراک پرسرعت (حجم دلخواه)**\n\n"
                f"📦 حجم: {gb} گیگ\n"
                f"💰 قابل پرداخت: {price_formatted} تومان\n\n"
                "───────────────\n"
                "💳 **کارت به کارت:**\n"
                "`6037997328226635`\n"
                "به نام: **محمد فتحی**\n\n"
                "⏳ پس از واریز، **فیش واریزی** را همینجا بفرستید."
            )
            user_custom_gb_cache[user_id] = gb
            bot.send_message(chat_id, invoice_text, parse_mode="Markdown")
            return
        except ValueError:
            bot.reply_to(message, "❌ لطفاً فقط یک عدد صحیح برای حجم (به گیگابایت) وارد کنید:")
            waiting_for_custom_gb[user_id] = True
            return

    if user_id == ADMIN_ID and ADMIN_ID in waiting_for_config:
        data = waiting_for_config[ADMIN_ID]
        target_user_id = data["user_id"]
        
        try:
            bot.send_message(
                target_user_id,
                f"🎉 **سرویس شما با موفقیت فعال شد!**\n\n"
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
        bot.send_message(chat_id, "از منوی زیر استفاده کنید:", reply_markup=main_inline_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_buy":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💳 **خرید حساب اختصاصی**\n\n⚡️ سرورهای پرسرعت و بهینه‌شده\nقیمت هر گیگ: **5,000 تومان**", reply_markup=buy_menu(), parse_mode="Markdown")
    
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
        if plan == "custom":
            bot.answer_callback_query(call.id, "حجم دلخواه")
            waiting_for_custom_gb[user_id] = True
            bot.send_message(chat_id, "✍️ لطفاً مقدار حجم دلخواه خود را به عدد (به گیگابایت) بفرستید:")
            return
            
        if plan == "1gb":
            gb, price = 1, "5,000"
        elif plan == "5gb":
            gb, price = 5, "25,000"
        elif plan == "20gb":
            gb, price = 20, "100,000"
            
        user_custom_gb_cache[user_id] = gb
        bot.answer_callback_query(call.id, f"پلن {gb} گیگی")
        invoice_text = (
            f"🛒 **فاکتور خرید اشتراک پرسرعت**\n\n📦 حجم: {gb} گیگ\n💰 قابل پرداخت: {price} تومان\n\n"
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

    elif call.data.startswith("verify_receipt_"):
        _, _, target_user_id, gb_val = call.data.split("_")
        bot.answer_callback_query(call.id, "رسید تایید شد.")
        
        try:
            bot.send_message(
                int(target_user_id),
                "✅ **رسید واریزی شما تایید شد!**\n\n⏳ لطفاً منتظر ارسال کانفیگ از طرف ربات باشید...",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🛠 ارسال دستی کانفیگ", callback_data=f"manual_{target_user_id}"),
            InlineKeyboardButton("🤖 ارسال خودکار از پنل", callback_data=f"auto_{target_user_id}_{gb_val}")
        )
        
        try:
            bot.edit_message_caption(
                chat_id=ADMIN_ID,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\n✅ **وضعیت: رسید تایید شد. روش ارسال را انتخاب کنید:**",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        except Exception:
            bot.send_message(ADMIN_ID, "✅ **رسید تایید شد. روش ارسال را انتخاب کنید:**", reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("auto_"):
        _, target_user_id, gb_val = call.data.split("_")
        bot.answer_callback_query(call.id, "در حال ساخت خودکار در پنل...")
        
        config_link = create_vless_config_via_panel(f"user_{target_user_id}", gb_val)
        
        if config_link:
            try:
                bot.send_message(
                    int(target_user_id),
                    f"🎉 **سرویس پرسرعت شما خودکار فعال گردید!**\n\n"
                    f"🔗 **لینک اشتراک اختصاصی شما:**\n`{config_link}`\n\n"
                    "از بخش «آموزش اتصال» می‌توانید نحوه راه‌اندازی را مشاهده کنید.",
                    parse_mode="Markdown"
                )
                bot.edit_message_caption(
                    chat_id=ADMIN_ID,
                    message_id=call.message.message_id,
                    caption=call.message.caption + f"\n\n🤖 **وضعیت: اکانت خودکار ساخته شد و ارسال گردید.**\n`{config_link}`",
                    parse_mode="Markdown"
                )
            except Exception:
                bot.send_message(ADMIN_ID, "❌ خطا در ارسال پیام به کاربر.")
        else:
            bot.send_message(ADMIN_ID, "❌ خطا در ساخت خودکار از پنل پاسارگاد!")

    elif call.data.startswith("manual_"):
        _, target_user_id = call.data.split("_")
        bot.answer_callback_query(call.id, "لطفاً لینک کانفیگ را بفرستید.")
        waiting_for_config[ADMIN_ID] = {"user_id": int(target_user_id)}
        bot.send_message(ADMIN_ID, "✍️ لطفاً لینک کانفیگ مورد نظر را همینجا ارسال کنید تا برای کاربر فرستاده شود:")

    elif call.data.startswith("reject_"):
        _, target_user_id = call.data.split("_")
        bot.answer_callback_query(call.id, "رد شد.")
        try:
            bot.send_message(int(target_user_id), "❌ فیش واریزی شما توسط ادمین رد شد.")
        except Exception:
            pass
        try:
            bot.edit_message_caption(
                chat_id=ADMIN_ID,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\n❌ **وضعیت: فیش رد شد.**",
                parse_mode="Markdown"
            )
        except Exception:
            bot.send_message(ADMIN_ID, "❌ فیش مورد نظر رد شد.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    if is_duplicate(message.message_id):
        return
    user = message.from_user
    gb_val = user_custom_gb_cache.get(user.id, 5)
    
    caption = f"📥 **فیش واریزی جدید!**\n\n👤 نام: {user.first_name}\n🆔 آیدی: `{user.id}`\n📦 حجم درخواستی: {gb_val} گیگ"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ تایید رسید", callback_data=f"verify_receipt_{user.id}_{gb_val}"),
        InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    bot.reply_to(message, "✅ فیش شما ارسال شد و به زودی پس از بررسی تایید می‌گردد.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True, interval=2)
