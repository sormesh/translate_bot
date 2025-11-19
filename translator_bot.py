import telebot
from telebot import types
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# ======= توکن ربات تلگرام =======
BOT_TOKEN = "8000043132:AAFxFYp3cMYj9YIBmlDSJUj2A8oAOtnNKII"
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

# ======= /start =======
def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("انگلیسی به فارسی", callback_data="en_to_fa")
    btn2 = types.InlineKeyboardButton("فارسی به انگلیسی", callback_data="fa_to_en")
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "سلام! خوش اومدی 👋✨\nلطفاً نوع ترجمه را انتخاب کن:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    show_main_menu(chat_id)

# ======= هندلر دکمه‌ها =======
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "en_to_fa":
        user_choice[chat_id] = "en_to_fa"
        bot.send_message(chat_id, "✅ حالت ترجمه: انگلیسی به فارسی انتخاب شد.\n\nحالا متن انگلیسی‌ات را ارسال کن:")
    elif call.data == "fa_to_en":
        user_choice[chat_id] = "fa_to_en"
        bot.send_message(chat_id, "✅ حالت ترجمه: فارسی به انگلیسی انتخاب شد.\n\nحالا متن فارسی‌ات را ارسال کن:")
    elif call.data == "back_to_menu":
        show_main_menu(chat_id)
    elif call.data == "continue":
        bot.send_message(chat_id, "لطفاً متن بعدی را ارسال کن ⚡️:")

# ======= دریافت متن =======
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_choice:
        bot.send_message(chat_id, "لطفاً اول /start را بزن و حالت ترجمه را انتخاب کن.")
        return

    choice = user_choice[chat_id]

    if choice == "en_to_fa":
        translated = translate_en_to_fa(text)
    else:
        translated = translate_fa_to_en(text)

    # ارسال ترجمه
    bot.send_message(chat_id, f"🤖 ترجمه:\n{translated}")

    # نمایش دکمه‌ها برای ادامه یا برگشت به منوی اصلی با متن ساده
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔄 برگشت به منوی اصلی", callback_data="back_to_menu")
    btn2 = types.InlineKeyboardButton("➡️ ادامه ترجمه", callback_data="continue")
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "می‌خوای چه کاری انجام بدی؟ انتخاب کن:", reply_markup=markup)

# ======= اجرای ربات =======
bot.infinity_polling()
