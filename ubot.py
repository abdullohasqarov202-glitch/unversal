import os
import telebot
from telebot import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN topilmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

# Reklama va spam uchun kalit so‘zlar
SPAM_KEYWORDS = [
    "t.me/", "http://", "https://", "bit.ly", "reklama", "advertisement", "sale", "promo"
]

# Foydalanuvchi ogohlantirishlarini saqlash (chat_id -> {user_id: warn_count})
warnings = {}
MAX_WARN = 3  # 3 marta ogohlantirilsa, avtomatik ban

# Xabar kelganda tekshirish
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_spam(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.lower()

    if any(keyword in text for keyword in SPAM_KEYWORDS):
        try:
            bot.delete_message(chat_id, message.message_id)

            # Ogohlantirishni yangilash
            if chat_id not in warnings:
                warnings[chat_id] = {}
            if user_id not in warnings[chat_id]:
                warnings[chat_id][user_id] = 0
            warnings[chat_id][user_id] += 1

            warn_count = warnings[chat_id][user_id]

            # 3 marta ogohlantirsa — avtomatik ban
            if warn_count >= MAX_WARN:
                bot.kick_chat_member(chat_id, user_id)
                bot.send_message(chat_id, f"⛔ {message.from_user.first_name} chatdan chiqarildi spam uchun!")
                warnings[chat_id][user_id] = 0
            else:
                bot.send_message(chat_id,
                                 f"⚠️ {message.from_user.first_name}, reklama yoki spam post o'chirildi! "
                                 f"({warn_count}/{MAX_WARN} ogohlantirish)")

        except Exception as e:
            print(f"[Xatolik o'chirishda] {e}")

# Admin buyruqlari
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Shu buyruqni ishlatish uchun xabarni javob sifatida tanlang.")
        return
    user = message.reply_to_message.from_user
    chat_id = message.chat.id

    if chat_id not in warnings:
        warnings[chat_id] = {}
    if user.id not in warnings[chat_id]:
        warnings[chat_id][user.id] = 0

    warnings[chat_id][user.id] += 1
    warn_count = warnings[chat_id][user.id]

    if warn_count >= MAX_WARN:
        try:
            bot.kick_chat_member(chat_id, user.id)
            bot.send_message(chat_id, f"⛔ {user.first_name} chatdan chiqarildi ogohlantirishlar uchun!")
            warnings[chat_id][user.id] = 0
        except Exception as e:
            bot.reply_to(message, f"❌ Xatolik: {e}")
    else:
        bot.reply_to(message, f"⚠️ {user.first_name} ogohlantirildi! ({warn_count}/{MAX_WARN})")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Shu buyruqni ishlatish uchun xabarni javob sifatida tanlang.")
        return
    user = message.reply_to_message.from_user
    try:
        bot.kick_chat_member(message.chat.id, user.id)
        bot.reply_to(message, f"⛔ {user.first_name} chatdan chiqarildi!")
        # Ogohlantirishni reset qilamiz
        chat_id = message.chat.id
        if chat_id in warnings and user.id in warnings[chat_id]:
            warnings[chat_id][user.id] = 0
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "➕ Botni guruhga qo‘shish",
        url=f"https://t.me/{bot.get_me().username}?startgroup=true"
    ))

    bot.send_message(
        message.chat.id,
        f"👋 Salom! Men reklamalarni avtomatik o'chiradigan botman.\n"
        f"Adminlar: /warn va /ban buyruqlarini ishlatish mumkin.\n"
        f"Spam avtomatik aniqlanadi va {MAX_WARN} ogohlantirishdan so'ng ban qilinadi.\n\n"
        f"Botni guruhingizga qo‘shish uchun quyidagi tugmani bosing:",
        reply_markup=markup
    )

print("✅ Bot ishga tushdi...")
bot.infinity_polling()
