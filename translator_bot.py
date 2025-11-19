import os
import telebot
from telebot import types
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# ======= گرفتن توکن تلگرام از Environment =======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ======= مدل ترجمه =======
model_name = "facebook/m2m100_418M"
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name)

# ======= ذخیره حالت کاربران =======
user_choice = {}  # chat_id → انتخاب کاربر

# ======= توابع ترجمه =======
def translate_en_to_fa(text):
    tokenizer.src_lang = "en"
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id("fa"))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

def translate_fa_to_en(text):
    tokenizer.src_lang = "fa"
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id("en"))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

# ======= منوی اصلی =======
def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("انگلیسی به فارسی", "فارسی به انگلیسی")
    bot.send_message(chat_id, "سلام! خوش اومدی 👋✨\nلطفاً نوع ترجمه را انتخاب کن:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    show_main_menu(chat_id)

# ======= دریافت متن و انتخاب حالت =======
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    # اگر حالت کاربر مشخص نیست
    if chat_id not in user_choice:
        if text == "انگلیسی به فارسی":
            user_choice[chat_id] = "en_to_fa"
            bot.send_message(chat_id, "✅ حالت ترجمه: انگلیسی به فارسی انتخاب شد.\n\nحالا متن انگلیسی‌ات را ارسال کن:")
        elif text == "فارسی به انگلیسی":
            user_choice[chat_id] = "fa_to_en"
            bot.send_message(chat_id, "✅ حالت ترجمه: فارسی به انگلیسی انتخاب شد.\n\nحالا متن فارسی‌ات را ارسال کن:")
        else:
            bot.send_message(chat_id, "لطفاً اول /start را بزن و یک گزینه انتخاب کن.")
        return

    # ترجمه متن
    choice = user_choice[chat_id]
    if choice == "en_to_fa":
        translated = translate_en_to_fa(text)
    else:
        translated = translate_fa_to_en(text)

    bot.send_message(chat_id, f"🤖 ترجمه:\n{translated}")

    # نمایش دکمه‌ها برای ادامه یا برگشت به منوی اصلی
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🔄 برگشت به منوی اصلی", "➡️ ادامه ترجمه")
    bot.send_message(chat_id, "می‌خوای چه کاری انجام بدی؟ انتخاب کن:", reply_markup=markup)

    # بررسی انتخاب بعدی
    def next_step_handler(message):
        next_choice = message.text
        if next_choice == "🔄 برگشت به منوی اصلی":
            user_choice.pop(chat_id, None)
            show_main_menu(chat_id)
        elif next_choice == "➡️ ادامه ترجمه":
            bot.send_message(chat_id, "⚡️ متن بعدی را ارسال کن:")
        else:
            bot.send_message(chat_id, "لطفاً یکی از گزینه‌ها را انتخاب کن.")

    bot.register_next_step_handler(message, next_step_handler)

# ======= اجرای ربات =======
print("robot is running")  # پیام اجرا در ترمینال
bot.infinity_polling(skip_pending=True)
