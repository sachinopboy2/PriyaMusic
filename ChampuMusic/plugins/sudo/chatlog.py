import random
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup
)
from ChampuMusic import app

JOINLOGS = -1002144355688  # Replace with your logging group/channel ID

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    bot_user = await client.get_me()

    for new_member in message.new_chat_members:
        if new_member.id == bot_user.id:
            added_by = (
                f"<a href='tg://user?id={message.from_user.id}'>👤{message.from_user.first_name}</a>"
                if message.from_user else "Unknown User"
            )
            chat_title = message.chat.title
            chat_id = message.chat.id
            chat_username = f"@{message.chat.username}" if message.chat.username else "Private Group"
            chat_link = (
                f"https://t.me/{message.chat.username}"
                if message.chat.username else None
            )

            log_text = (
                f"<b>🤖 Bot Added to a New Chat!</b>\n\n"
                f"<b>📌 Chat Name:</b> <code>{chat_title}</code>\n"
                f"<b>🆔 Chat ID:</b> <code>{chat_id}</code>\n"
                f"<b>🔗 Username:</b> {chat_username}\n"
                f"<b>➕ Added By:</b> {added_by}"
            )

            buttons = []
            if chat_link:
                buttons.append([
                    InlineKeyboardButton("➤ Open Group", url=chat_link)
                ])

            try:
                await client.send_message(
                    JOINLOGS,
                    text=log_text,
                    reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"[JOINLOG ERROR] Failed to send join log: {e}")

            # Optional welcome message in group
            try:
                await message.reply_text(
                    f"Thanks for adding me to <b>{chat_title}</b>!\nUse <code>/help</code> to get started.",
                )
            except Exception as e:
                print(f"[WELCOME ERROR] Failed to send welcome message: {e}")
