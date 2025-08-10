import os
import telebot
from googletrans import Translator
from telebot import types
import logging

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Railwaydan oladi
DEFAULT_LANG = 'en'

SUPPORTED_LANGS = {
    'en': 'English',
    'uz': "Uzbek",
    'ru': 'Russian',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'it': 'Italian'
}

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
user_targets = {}

def get_target(chat_id):
    return user_targets.get(chat_id, DEFAULT_LANG)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    txt = ("Salom! Men tarjimon botiman.\n\n"
           "/langs - tillar ro'yxati\n"
           "/set <kod> - til tanlash (masalan: /set ru)\n"
           "/translate <matn> - matnni tarjima qilish\n\n"
           "Oddiy xabar yuborsangiz, men uni siz tanlagan tilga tarjima qilaman.")
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=['langs'])
def list_langs(message):
    lines = [f"{code} — {name}" for code, name in SUPPORTED_LANGS.items()]
    bot.send_message(message.chat.id, "Qo'llab-quvvatlanadigan tillar:\n" + "\n".join(lines))

@bot.message_handler(commands=['set'])
def set_lang(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Til kodini kiriting. Masalan: /set ru")
        return
    code = parts[1].lower()
    if code not in SUPPORTED_LANGS:
        bot.reply_to(message, "Bunday til qo'llab-quvvatlanmaydi. /langs ni tekshiring.")
        return
    user_targets[message.chat.id] = code
    bot.reply_to(message, f"Maqsad tili {SUPPORTED_LANGS[code]} ({code}) sifatida o'rnatildi.")

@bot.message_handler(commands=['translate'])
def force_translate(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Matn yuboring: /translate Hello world")
        return
    text = parts[1]
    dest = get_target(message.chat.id)
    try:
        res = translator.translate(text, dest=dest)
        out = f"Tarjima ({res.src} -> {dest}):\n{res.text}"
    except Exception as e:
        logging.exception("Translate error")
        out = "Tarjima amalga oshmadi."
    bot.reply_to(message, out)

@bot.message_handler(func=lambda m: True)
def translate_incoming(message):
    if message.text and message.text.startswith('/'):
        return
    dest = get_target(message.chat.id)
    try:
        res = translator.translate(message.text, dest=dest)
        out = f"Tarjima ({res.src} -> {dest}):\n{res.text}"
    except Exception as e:
        logging.exception("Translate error")
        out = "Tarjima amalga oshmadi."
    bot.reply_to(message, out)

if __name__ == '__main__':
    bot.infinity_polling()
