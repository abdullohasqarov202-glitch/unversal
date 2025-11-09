import os
import telebot
from telebot import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN topilmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

SPAM_KEYWORDS = [
    "t.me/", "http://", "https://", "bit.ly", "reklama", "advertisement", "sale", "promo"
]

# Xabar kelganda tekshirish
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_spam(message):
    text = message.text.lower()
    if any(keyword in text for keyword in SPAM_KEYWORDS):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             f"🚫 {message.from_user.first_name}, reklama yoki spam post o'chirildi!")
        except Exception as e:
            print(f"[Xatolik o'chirishda] {e}")

# Admin buyruqlari
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Shu buyruqni ishlatish uchun xabarni javob sifatida tanlang.")
        return
    user = message.reply_to_message.from_user
    bot.reply_to(message, f"⚠️ {user.first_name} ogohlantirildi!")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Shu buyruqni ishlatish uchun xabarni javob sifatida tanlang.")
        return
    user = message.reply_to_message.from_user
    try:
        bot.kick_chat_member(message.chat.id, user.id)
        bot.reply_to(message, f"⛔ {user.first_name} chatdan chiqarildi!")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "👋 Salom! Men reklamalarni avtomatik o'chiradigan botman.\n"
                     "Adminlar: /warn va /ban buyruqlarini ishlatish mumkin.")

print("✅ Bot ishga tushdi...")
bot.infinity_polling()
