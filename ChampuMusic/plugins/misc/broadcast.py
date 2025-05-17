import time
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait, RPCError

from ChampuMusic import app
from ChampuMusic.misc import SUDOERS
from ChampuMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from ChampuMusic.utils.decorators.language import language
from ChampuMusic.utils.formatters import alpha_to_int
from config import adminlist


REQUEST_LIMIT = 50
BATCH_SIZE = 500
BATCH_DELAY = 2
MAX_RETRIES = 2

# Global broadcast result tracker
last_broadcast_result = {}

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_command(client, message, _):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message you want to broadcast.")

    command_text = message.text.lower()
    mode = "forward" if "-forward" in command_text else "copy"

    if "-all" in command_text:
        target_users = await get_served_users()
        target_chats = await get_served_chats()
    elif "-users" in command_text:
        target_chats = []
        target_users = await get_served_users()
    elif "-chats" in command_text:
        target_chats = await get_served_chats()
        target_users = []
    else:
        return await message.reply_text("Please use a valid tag: `-all`, `-users`, `-chats`.")

    if not target_chats and not target_users:
        return await message.reply_text("No targets found for broadcast.")

    start_time = time.time()
    sent_count, failed_count = 0, 0
    targets = target_chats + target_users
    total_targets = len(targets)

    status_msg = await message.reply_text(f"Broadcast started in `{mode}` mode...\n\nProgress: `0%`")

    async def send_with_retries(chat_id):
        nonlocal sent_count, failed_count
        for attempt in range(MAX_RETRIES):
            try:
                if mode == "forward":
                    await app.forward_messages(
                        chat_id,
                        message.chat.id,
                        message.reply_to_message.id,
                        as_copy=False  # Important: Don't hide sender
                    )
                else:
                    await message.reply_to_message.copy(chat_id)
                sent_count += 1
                return
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except RPCError:
                await asyncio.sleep(0.5)
        failed_count += 1

    async def broadcast_targets(target_list):
        nonlocal sent_count, failed_count
        for i in range(0, len(target_list), BATCH_SIZE):
            batch = target_list[i:i + BATCH_SIZE]
            tasks = []
            for chat_id in batch:
                if len(tasks) >= REQUEST_LIMIT:
                    await asyncio.gather(*tasks)
                    tasks.clear()
                tasks.append(send_with_retries(chat_id))
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(BATCH_DELAY)

            # Update progress and ETA after each batch
            percent = round((sent_count + failed_count) / total_targets * 100, 2)
            elapsed = time.time() - start_time
            eta = (elapsed / (sent_count + failed_count)) * (total_targets - (sent_count + failed_count)) if sent_count + failed_count > 0 else 0
            eta_formatted = f"{int(eta//60)}m {int(eta%60)}s"

            progress_bar = f"[{'█' * int(percent//5)}{'░' * (20-int(percent//5))}]"
            await status_msg.edit_text(
                f"<b>🔔 Broadcast Progress:</b>\n"
                f"{progress_bar} <code>{percent}%</code>\n"
                f"✅ Sent: <code>{sent_count}</code> 🟢\n"
                f"⛔ Failed: <code>{failed_count}</code> 🔴\n"
                f"🕰 ETA: <code>{eta_formatted}</code> ⏳"
            )

    await broadcast_targets(targets)

    total_time = round(time.time() - start_time, 2)

    final_summary = (
        f"<b>✅Broadcast Report📢</b>\n\n"
        f"Mode: <code>{mode}</code>\n"
        f"Total Targets: <code>{total_targets}</code>\n"
        f"Successful: <code>{sent_count}</code> 🟢\n"
        f"Failed: <code>{failed_count}</code> 🔴\n"
        f"Time Taken: <code>{total_time}</code> seconds ⏰"
    )

    await status_msg.edit_text(final_summary)

    # Store last result globally for /broadcaststats command
    last_broadcast_result.update({
        "mode": mode,
        "total": total_targets,
        "sent": sent_count,
        "failed": failed_count,
        "time": total_time
    })

# Optional: /broadcaststats command
@app.on_message(filters.command("broadcaststats") & SUDOERS)
async def broadcast_stats(_, message):
    if not last_broadcast_result:
        return await message.reply_text("No broadcast run yet.")

    res = last_broadcast_result
    await message.reply_text(
        f"<b>📜Last Broadcast Report:</b>\n\n"
        f"Mode: <code>{res['mode']}</code>\n"
        f"Total Targets: <code>{res['total']}</code>\n"
        f"Successful: <code>{res['sent']}</code> 🟢\n"
        f"Failed: <code>{res['failed']}</code> 🔴\n"
        f"Time Taken: <code>{res['time']}</code> seconds ⏰"
    )

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())
