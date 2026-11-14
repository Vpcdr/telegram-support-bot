import os
import telebot

# توکن ربات تلگرام خود را به جای متن زیر قرار دهید
TOKEN = 'TOKEN_BOT_KHOD_RA_INJA_VARD_KONID'
bot = telebot.TeleBot(TOKEN)


# پاسخ به دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, 'سلام! ربات شما با موفقیت روشن و آماده به کار شد.')


# پاسخ به پیام‌های متنی کاربران
@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, 'پیام شما دریافت شد!')


# اجرای ربات
if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()
