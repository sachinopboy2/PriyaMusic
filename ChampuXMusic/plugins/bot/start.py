import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from ChampuXMusic import app
from ChampuXMusic.misc import _boot_, SUDOERS
from ChampuXMusic.plugins.sudo.sudoers import sudoers_list
from ChampuXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    get_assistant,
)
from ChampuXMusic.utils.decorators.language import LanguageStart
from ChampuXMusic.utils.formatters import get_readable_time
from ChampuXMusic.utils.inline import alive_panel, help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
    else:

        try: 
            out = private_panel(_)
            if message.chat.photo:

                userss_photo = await app.download_media(
                    message.chat.photo.big_file_id,
                )
            else:
                userss_photo = "ChampuXMusic/assets/nodp.jpg"
            if userss_photo:
                chat_photo = userss_photo
            chat_photo = userss_photo if userss_photo else config.START_IMG_URL

        except AttributeError:
            chat_photo = "ChampuXMusic/assets/nodp.jpg"
        await message.reply_photo(
            photo=chat_photo,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOGGER_ID,
                f"{message.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ᴜsᴇʀ ɪᴅ :** {sender_id}\n**ᴜsᴇʀ ɴᴀᴍᴇ:** {sender_name}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    try:
        chat_id = message.chat.id
        try:
            # Try downloading the group's photo
            groups_photo = await client.download_media(
                message.chat.photo.big_file_id, file_name=f"chatpp{chat_id}.png"
            )
            chat_photo = groups_photo if groups_photo else config.START_IMG_URL
        except AttributeError:
            # If there's no chat photo, use the default image
            chat_photo = config.START_IMG_URL

        # Get the alive panel and uptime
        out = alive_panel(_)
        uptime = int(time.time() - _boot_)

        # Send the response with the group photo or fallback to START_IMG_URL
        if chat_photo:
            await message.reply_photo(
                photo=chat_photo,
                caption=_["start_7"].format(client.mention, get_readable_time(uptime)),
                reply_markup=InlineKeyboardMarkup(out),
            )
        else:
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["start_7"].format(client.mention, get_readable_time(uptime)),
                reply_markup=InlineKeyboardMarkup(out),
            )

        # Add the chat to the served chat list
        return await add_served_chat(chat_id)

    except Exception as e:
        print(f"Error: {e}")


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    # Handle new chat members
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)

            # If bot itself joins the chat
            if member.id == client.id:
                try:
                    groups_photo = await client.download_media(
                        message.chat.photo.big_file_id, file_name=f"chatpp{chat_id}.png"
                    )
                    chat_photo = groups_photo if groups_photo else config.START_IMG_URL
                except AttributeError:
                    chat_photo = config.START_IMG_URL

                userbot = await get_assistant(chat_id)
                out = alive_panel(_)
                await message.reply_photo(
                    photo=chat_photo,
                    caption=_["start_8"],
                    reply_markup=InlineKeyboardMarkup(out),
                )

            # Handle owner joining
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_3"].format(client.mention, member.mention)
                )

            # Handle SUDOERS joining
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_4"].format(client.mention, member.mention)
                )
            return

        except Exception as e:
            print(f"Error: {e}")
            return

