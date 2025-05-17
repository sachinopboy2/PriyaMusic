"""import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from ChampuMusic import app
from ChampuMusic.misc import SUDOERS
from ChampuMusic.utils import get_readable_time
from ChampuMusic.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from ChampuMusic.utils.decorators.language import language
from ChampuMusic.utils.extraction import extract_user
from config import BANNED_USERS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])

    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))

    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)

    served_chats = await get_served_chats()  # Use the new function
    served_chat_ids = [chat["_id"] for chat in served_chats]

    time_expected = get_readable_time(len(served_chat_ids))
    mystic = await message.reply_text(
        f"🚫 Global Ban initiated!\n\n"
        f"⚠️ User: {user.mention} has been banned globally!\n\n"
        f"🗂 Affected Chats: {len(served_chat_ids)}\n"
        f"⏳ Expected Time: {time_expected}\n\n"
        f"🔐 Banned by: {message.from_user.mention}\n"
        f"🔄 Progress: ⏳ 0% Banning...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel Ban", callback_data=f"cancel_ban_{user.id}")]
        ])
    )

    number_of_chats = 0
    for chat_id in served_chat_ids:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
            # Calculate the percentage
            percentage = (number_of_chats / len(served_chat_ids)) * 100
            await mystic.edit_text(
                f"🚫 Global Ban in Progress!\n\n"
                f"⚠️ User: {user.mention} has been banned globally!\n\n"
                f"🗂 Affected Chats: {len(served_chat_ids)}\n"
                f"⏳ Expected Time: {time_expected}\n\n"
                f"🔐 Banned by: {message.from_user.mention}\n"
                f"🔄 Progress: ⏳ {int(percentage)}% Banning...",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel Ban", callback_data=f"cancel_ban_{user.id}")]
                ])
            )
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except Exception as e:
            continue

    await add_banned_user(user.id)

    await message.reply_text(
        f"🔒 User: {user.mention} has been banned successfully in {number_of_chats} chats!\n"
        f"⏳ Banned by: {message.from_user.mention}\n"
        f"💬 Chat Title: {message.chat.title}\n"
        f"🔐 User ID: {user.id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Banned Users", callback_data="view_banned_users")]
        ])
    )
    await mystic.delete()


@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    is_gbanned = await is_gbanned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))

    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)

    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        # Convert chat ID to a regular integer
        served_chats.append(int(chat["_id"]))  # _id should be the correct key for MongoDB

    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(
        f"🔓 Global Unban initiated!\n\n"
        f"✅ User: {user.mention} is being unbanned globally!\n\n"
        f"🔄 Progress: ⏳ 0% Unbanning...\n\n"
        f"🗂 Reinstating in: {len(served_chats)} chats\n"
        f"⏳ Expected Time: {time_expected}\n\n"
        f"🎉 Unbanned by: {message.from_user.mention}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel Unban", callback_data=f"cancel_unban_{user.id}")]
        ])
    )

    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
            # Calculate the percentage
            percentage = (number_of_chats / len(served_chats)) * 100
            await mystic.edit_text(
                f"🔓 Global Unban in Progress!\n\n"
                f"✅ User: {user.mention} has been unbanned globally!\n\n"
                f"🔄 Progress: ⏳ {int(percentage)}% Unbanning...\n\n"
                f"🗂 Reinstating in: {len(served_chats)} chats\n"
                f"⏳ Expected Time: {time_expected}\n\n"
                f"🎉 Unbanned by: {message.from_user.mention}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel Unban", callback_data=f"cancel_unban_{user.id}")]
                ])
            )
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue

    await remove_gban_user(user.id)

    await message.reply_text(
        f"✅ **User**: {user.mention} has been unbanned from **{number_of_chats}** chats!\n"
        f"🎉 **Unbanned by**: {message.from_user.mention}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Banned Users", callback_data="view_banned_users")]
        ])
    )
    await mystic.delete()



@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(
            "📜 Global Banned Users List:\n\n"
            "🚫 No users are currently banned."
        )

    mystic = await message.reply_text("📜 Fetching Global Banned Users...")
    msg = "📜 Global Banned Users List:\n\n"
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue

    if count == 0:
        return await mystic.edit_text(
            "📜 Global Banned Users List:\n\n🚫 No banned users found!"
        )
    else:
        return await mystic.edit_text(msg, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Refresh List", callback_data="refresh_gban_list")]
        ]))

@app.on_callback_query()
async def on_callback_query(client, callback_query):
    data = callback_query.data
    user = callback_query.from_user

    if data.startswith("cancel_ban_"):
        user_id = int(data.split("_")[2])
        # Handle cancel ban action (remove from banning process or notify admin)
        await callback_query.answer(f"❌ Ban process for {user_id} canceled.")
        return

    if data.startswith("cancel_unban_"):
        user_id = int(data.split("_")[2])
        # Handle cancel unban action (remove from unbanning process or notify admin)
        await callback_query.answer(f"❌ Unban process for {user_id} canceled.")
        return

    if data == "refresh_gban_list":
        # Refresh the list of global banned users
        await gbanned_list(client, callback_query.message, _)
        return


from pyrogram import filters
from pyrogram.types import Message

# Ensure BANNED_USERS is a set of banned user IDs
BANNED_USERS = set()  # Example: BANNED_USERS = {12345, 67890}

# Helper function to check if a user is globally banned
async def is_banned_user(user_id):
    return user_id in BANNED_USERS

# Listen to all messages in the group
@app.on_message(filters.group)  # This will apply to all groups
async def delete_gbanned_user_message(client, message: Message):
    if not message.from_user:
        return

    user = message.from_user
    # Check if the user is globally banned
    is_gbanned = await is_banned_user(user.id)

    if is_gbanned:
        # Check if the user is an admin in the current group
        chat_member = await client.get_chat_member(message.chat.id, user.id)
        if chat_member.status in ["administrator", "creator"]:  # Check if the user is an admin
            # Delete the message
            await message.delete()

            # Optionally, send a notification to the group or log it
            await message.reply_text(f"⚠️ The message from the globally banned user {user.mention} was deleted.", quote=True)
"""
