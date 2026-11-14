import os
import telebot
from flask import Flask
import threading

TOKEN = '9177015792:AAGugV7I4lr-I_8P43zPR4LL15-dSwUlc5I'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# مسیر اصلی وب‌سایت برای این که رندر پورت را باز ببیند و خطا ندهد
@server.route('/')
def index():
    return "Bot is running!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! ربات با موفقیت روشن و آماده به کار شد.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"پیام شما دریافت شد: {message.text}")

# اجرای ربات در پس‌زمینه با متد infinity_polling
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # استارت کردن ربات در یک ترد جداگانه
    t = threading.Thread(target=run_bot)
    t.start()
    
    # استارت کردن سرور Flask برای باز نگه داشتن پورت رندر
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
