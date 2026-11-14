#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=============================================================
راهنما: توکن ربات خود را به عنوان Environment Variable با نام TOKEN 
در هاست (مثل Render) تنظیم کنید، یا به صورت موقت مستقیماً جایگزین کنید.
=============================================================
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# دریافت توکن از متغیرهای محیطی سیستم/هاست (یا قرار دادن مستقیم توکن در صورت نیاز)
TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN_HERE")

# آیدی عددی ادمین
ADMIN_ID = 7433883194

# تنظیمات لاگ‌گرفتن
logging.basicConfig(level=logging.INFO)
router = Router()

# دیکشنری برای نگهداری رابطه (آیدی پیام کپی‌شده نزد ادمین -> آیدی عددی کاربر)
message_map = {}


# حالت‌های مکالمه (FSM)
class SupportState(StatesGroup):
    waiting_for_message = State()


# متن دکمه‌ها و اطلاعات تماس
CONTACT_TEXT = (
    "📞 راه‌های ارتباطی با ما:\n"
    "تلگرام پشتیبانی: @vgpcdr\n"
    "موبایل: 09159813368\n"
    "موبایل دوم: 09371226509\n"
    "اینستاگرام: @vpcdr\n"
    "ربات ارتباط: @sangsorakhertebatbot"
)

INSTA_TEXT = (
    "پیج اینستاگرام ما 👇\n" "https://instagram.com/vpcdr"
)

ABOUT_TEXT = (
    "سنگ‌سوراخ‌زیبا ✨\n"
    "برای سفارش، مشاوره و پشتیبانی از همین ربات پیام بدید."
)

SUPPORT_PROMPT_TEXT = (
    "پیامت رو بنویس، مستقیم میرسه دست پشتیبانی 👇\n"
    "متن، عکس، ویس، ویدیو و فایل هم می‌تونی بفرستی."
)

# کیبورد اصلی شیشه‌ای (Inline Keyboard)
main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 ارسال پیام به پشتیبانی", callback_data="send_to_support"
            )
        ],
        [
            InlineKeyboardButton(text="📞 تماس با ما", callback_data="contact_us"),
            InlineKeyboardButton(text="📸 اینستاگرام", callback_data="instagram"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ درباره ما", callback_data="about_us"),
        ],
    ]
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        "سلام 👋 به ربات «ارتباط با ما ( سنگ‌سوراخ‌زیبا )» خوش اومدی\n"
        "سوالت رو بنویس یا از دکمه‌های پایین استفاده کن.\n"
        "می‌تونی متن، عکس، ویس، ویدیو و فایل هم بفرستی."
    )
    await message.answer(welcome_text, reply_markup=main_keyboard)


@router.callback_query(F.data == "contact_us")
async def cb_contact(callback: CallbackQuery):
    await callback.message.answer(CONTACT_TEXT)
    await callback.answer()


@router.callback_query(F.data == "instagram")
async def cb_instagram(callback: CallbackQuery):
    await callback.message.answer(INSTA_TEXT)
    await callback.answer()


@router.callback_query(F.data == "about_us")
async def cb_about(callback: CallbackQuery):
    await callback.message.answer(ABOUT_TEXT)
    await callback.answer()


@router.callback_query(F.data == "send_to_support")
async def cb_send_to_support(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportState.waiting_for_message)
    await callback.message.answer(SUPPORT_PROMPT_TEXT)
    await callback.answer()


@router.message(F.chat.id == ADMIN_ID)
async def admin_handler(message: Message):
    """مدیریت پاسخ‌های ادمین به کاربران"""
    if not message.reply_to_message:
        return

    replied_msg = message.reply_to_message
    map_key = (message.chat.id, replied_msg.message_id)

    target_user_id = message_map.get(map_key)

    if not target_user_id:
        await message.reply(
            "❌ نتونستم کاربر رو پیدا کنم. روی پیام دوم (پیام کپی شده کاربر) Reply کن."
        )
        return

    try:
        sent_msg = await message.send_copy(chat_id=target_user_id)
        message_map[(ADMIN_ID, sent_msg.message_id)] = target_user_id
        await message.reply("✅ جوابت برای کاربر ارسال شد.")
    except Exception as e:
        await message.reply(f"❌ خطا در ارسال پیام به کاربر: {e}")


@router.message(F.chat.id != ADMIN_ID)
async def user_message_handler(message: Message, state: FSMContext, bot: Bot):
    """دریافت پیام از کاربر و ارسال آن به ادمین"""
    if message.text in [
        "📞 تماس با ما",
        "📸 اینستاگرام",
        "ℹ️ درباره ما",
        "💬 ارسال پیام به پشتیبانی",
    ]:
        return

    user = message.from_user
    user_full_name = user.full_name or "بدون نام"
    username = f"@{user.username}" if user.username else "ندارد"
    user_id = user.id

    await state.set_state(SupportState.waiting_for_message)

    info_text = (
        f"📩 پیام جدید از کاربر:\n"
        f"نام: {user_full_name}\n"
        f"آیدی: {username}\n"
        f"کد کاربر: {user_id}"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=info_text)

    try:
        copied_message = await message.send_copy(chat_id=ADMIN_ID)
        message_map[(ADMIN_ID, copied_message.message_id)] = user_id
    except Exception as e:
        logging.error(f"Error copying message to admin: {e}")

    await message.answer("پیامت رسید ✅ به زودی جواب میدیم.")


async def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ هشدار: توکن ربات تنظیم نشده است!")

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
