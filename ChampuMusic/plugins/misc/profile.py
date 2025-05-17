from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from operator import itemgetter
from ChampuMusic import app
from ChampuMusic.utils.database import song_stats_db
import random

# Default placeholder image
DEFAULT_IMAGE = [
    "https://graph.org/file/f20072ed0125e05c4a179-749b57b82ab375adfb.jpg",
    "https://graph.org/file/742d864c80feee4fa8476-a32e01adeea7b7df18.jpg",
    "https://graph.org/file/5146d19a7e8f4a4bf135e-2c1a0899cc2de6efd4.jpg",
    "https://graph.org/file/4b17ae416c6501cb8f4b6-3f5f9d6f4edb90e14a.jpg",
    "https://graph.org/file/671aa8e4b175394089634-885eaf7d16ee0ab42f.jpg", 
    "https://graph.org/file/c0433c883bfa2f9a2cc8c-cc1d7f1b6e5fecdf20.jpg", 
    "https://telegra.ph/file/e5340836c6f109e68ccdb-f0ba945acf333f87cc.jpg"
]


# ───── Helpers ─────────────────────────────────────────

async def update_song_count(group_id: int, user_id: int):
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        await song_stats_db.update_one(
            {"group_id": group_id},
            {
                "$inc": {
                    "overall_count": 1,
                    f"daily.{today}": 1,
                    f"users.{user_id}": 1
                }
            },
            upsert=True
        )
        print("Song count updated successfully!")
    except Exception as e:
        print(f"Error updating song count: {e}")

async def get_user_profile(user_id: int):
    user_counter = {}
    async for rec in song_stats_db.find({}):
        for u, c in rec.get("users", {}).items():
            user_counter[u] = user_counter.get(u, 0) + c

    sorted_users = sorted(user_counter.items(), key=itemgetter(1), reverse=True)
    count = user_counter.get(str(user_id), 0)
    rank = next((i+1 for i, (u, _) in enumerate(sorted_users) if u == str(user_id)), None)
   
    print(f"User counter: {user_counter}")
    return count, rank
    
# ───── Handlers ────────────────────────────────────────

@app.on_message(filters.command("leaderboard") & filters.group)
async def leaderboard_menu(client: Client, message: Message):
    print("Leaderboard command received")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Top Groups Overall", callback_data="overall_songs")],
        [InlineKeyboardButton("📅 Top Groups Today", callback_data="today_songs")],
        [InlineKeyboardButton("📊 Top Groups This Week", callback_data="weekly_songs")],
        [InlineKeyboardButton("🏆 Top Music Lovers", callback_data="top_users")], 
        [InlineKeyboardButton("⏹ Close", callback_data="close_profile")]
    ])
    await message.reply_text(
    "🎶 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗟𝗲𝗮𝗱𝗲𝗿𝗯𝗼𝗮𝗿𝗱 𝗠𝗲𝗻𝘂\n\n"
    "Discover the top-performing groups and users based on their song plays!\n\n"
    "Select a category below to view:", 
    reply_markup=kb
)


@app.on_message(filters.command("profile") & filters.group)
async def user_profile(client: Client, message: Message):
  uid = message.from_user.id
  count, rank = await get_user_profile(uid)

  try:
    photos = await client.get_profile_photos(uid, limit=1)
    if photos.total_count > 0:
      photo = photos.photos[0][0].file_id
    else:
      photo = random.choice(DEFAULT_IMAGE)
  except Exception as e:
    print(e)
    photo = random.choice(DEFAULT_IMAGE)

  uname = message.from_user.username or "N/A"
  name = message.from_user.first_name

  if count == 0:
    text = (
      f"🎶 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗠𝘂𝘀𝗶𝗰 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 🎶\n\n"
      f"👤 Name: {name}\n"
      f"✨ Username: @{uname}\n"
      f"🆔 User ID: <code>{uid}</code>\n"
      f"🎧 Songs Played: <code>0</code>\n"
      f"📊 Rank: <code>Unranked</code>\n"
      f"💡 You haven't played any songs yet. Start vibing with the playlist!\n"
            f"🔻 Powered by: {app.mention}"
    )
  else:
    text = (
      f"🎶 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗠𝘂𝘀𝗶𝗰 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 🎶\n\n"
      f"👤 Name: {name}\n"
      f"✨ Username: @{uname}\n"
      f"🆔 User ID: <code>{uid}</code>\n"
      f"🎧 Songs Played: <code>{count}</code>\n"
      f"📊 Rank: <code>#{rank}</code>\n\n"
      f"<b>🔥 Keep the beats alive!</b>"
    )

  kb = InlineKeyboardMarkup(
    [[InlineKeyboardButton("⏹ close", callback_data="close_profile")]]
  )

  await message.reply_photo(photo, caption=text, reply_markup=kb)

@app.on_callback_query(filters.regex("^close_profile$"))
async def close_profile(client: Client, cq: CallbackQuery):
    await cq.message.delete()

@app.on_callback_query(filters.regex("^(overall_songs|today_songs|weekly_songs|top_users)$"))
async def leaderboard_callback(client: Client, cq: CallbackQuery):
    data = cq.data
    print(f"Callback received: {data}")
    if data == "overall_songs":
        await show_overall_leaderboard(client, cq)
    elif data == "today_songs":
        await show_today_leaderboard(client, cq)
    elif data == "weekly_songs":
        await show_weekly_leaderboard(client, cq)
    elif data == "top_users":
        await show_top_users(client, cq)

# ───── Leaderboard Views ───────────────────────────────

async def show_overall_leaderboard(client: Client, cq: CallbackQuery):
  leaderboard = []
  total_songs = 0
  async for record in song_stats_db.find({}):
    count = record.get("overall_count", 0)
    leaderboard.append((record["group_id"], count))
    total_songs += count

  leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
  if not leaderboard:
    return await cq.message.edit_text("No data found!")

  text = "📈 𝗚𝗟𝗢𝗕𝗔𝗟 𝗧𝗢𝗣 𝗚𝗥𝗢𝗨𝗣𝗦 | 🌍\n\n"
  for i, (group_id, count) in enumerate(leaderboard, 1):
    try:
      chat = await client.get_chat(group_id)
      text += f"<b>{i}.</b> 👥 {chat.title} — <code>{count}</code> songs\n"
    except:
      text += f"<b>{i}.</b> 👥 Unknown[{group_id}] — <code>{count}</code> songs\n"

  text += f"\n🎵 𝗧𝗼𝘁𝗮𝗹 𝗣𝗹𝗮𝘆𝗲𝗱 𝗦𝗼𝗻𝗴𝘀: <code>{total_songs}</code>"
  text += f"\n♨️ Powered By : {app.mention}"

  kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
  await cq.message.edit_text(text, reply_markup=kb)

async def show_today_leaderboard(client: Client, cq: CallbackQuery):
  today = datetime.utcnow().strftime("%Y-%m-%d")
  leaderboard = []
  total_songs = 0
  async for record in song_stats_db.find({}):
    count = record.get("daily", {}).get(today, 0)
    leaderboard.append((record["group_id"], count))
    total_songs += count

  leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
  if not leaderboard or leaderboard[0][1] == 0:
    return await cq.message.edit_text("No songs played today!")

  text = "📅 𝗧𝗢𝗣 𝗚𝗥𝗢𝗨𝗣𝗦 𝘁𝗼𝗱𝗮𝘆 | 🌍\n[𝗧𝗼𝗱𝗮𝘆’𝘀 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱] \n\n"
  for i, (group_id, count) in enumerate(leaderboard, 1):
    try:
      chat = await client.get_chat(group_id)
      text += f"<b>{i}.</b> 👥 {chat.title} — <code>{count}</code> songs\n"
    except:
      text += f"<b>{i}.</b> 👥 Unknown[{group_id}] — <code>{count}</code> songs\n"

  text += f"\nTotal Played Songs: <code>{total_songs}</code>"
  text += f"\nPowered By : {app.mention}"

  kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
  await cq.message.edit_text(text, reply_markup=kb)

async def show_weekly_leaderboard(client: Client, cq: CallbackQuery):
  today = datetime.utcnow()
  dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
  leaderboard = []
  total_songs = 0

  async for record in song_stats_db.find({}):
    total = sum(record.get("daily", {}).get(d, 0) for d in dates)
    leaderboard.append((record["group_id"], total))
    total_songs += total

  leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
  if not leaderboard or leaderboard[0][1] == 0:
    return await cq.message.edit_text("No songs played this week!")

  text = "📊 𝗧𝗢𝗣 𝗚𝗥𝗢𝗨𝗣𝗦 𝗪𝗘𝗘𝗞 | 🌍\n𝗧𝗵𝗶𝘀 𝗪𝗲𝗲𝗸’𝘀 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱 📊\n\n"
  for i, (group_id, count) in enumerate(leaderboard, 1):
    try:
      chat = await client.get_chat(group_id)
      text += f"<b>{i}.</b> 👥 {chat.title} — <code>{count}</code> songs\n"
    except:
      text += f"<b>{i}.</b> 👥 Unknown[{group_id}] — <code>{count}</code> songs\n"

  text += f"\n🎵 𝗧𝗼𝘁𝗮𝗹 𝗣𝗹𝗮𝘆𝗲𝗱 𝗦𝗼𝗻𝗴𝘀: <code>{total_songs}</code>"
  text += f"\n♨️ Powered By : {app.mention}"

  kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
  await cq.message.edit_text(text, reply_markup=kb)


async def show_top_users(client: Client, cq: CallbackQuery):
  user_counter = {}
  total_songs = 0
  async for record in song_stats_db.find({}):
    for user_id, count in record.get("users", {}).items():
      user_counter[user_id] = user_counter.get(user_id, 0) + count
      total_songs += count

  leaderboard = sorted(user_counter.items(), key=itemgetter(1), reverse=True)[:10]
  if not leaderboard:
    return await cq.message.edit_text("No user data found!")

  text = "📈 𝗧𝗼𝗽 𝗠𝘂𝘀𝗶𝗰 𝗟𝗼𝘃𝗲𝗿𝘀 | 🌍\n\n"
  for i, (user_id, count) in enumerate(leaderboard, 1):
    try:
      user = await client.get_users(int(user_id))
      text += f"<b>{i}.</b> <a href='tg://user?id={user.id}'>👤 {user.first_name}</a> — <code>{count}</code> songs\n"
    except:
      text += f"<b>{i}.</b>👤 Unknown[{user_id}] — <code>{count}</code> songs\n"

  text += f"\n🎵 𝗧𝗼𝘁𝗮𝗹 𝗣𝗹𝗮𝘆𝗲𝗱 𝗦𝗼𝗻𝗴𝘀: <code>{total_songs}</code>"
  text += f"\n♨️ Powered By : {app.mention}"

  kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
  await cq.message.edit_text(text, reply_markup=kb)

@app.on_callback_query(filters.regex("^back_leaderboard$"))
async def back_to_leaderboard(client: Client, cq: CallbackQuery):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Top Groups Overall", callback_data="overall_songs")],
        [InlineKeyboardButton("📅 Top Groups Today", callback_data="today_songs")],
        [InlineKeyboardButton("📊 Top Groups This Week", callback_data="weekly_songs")],
        [InlineKeyboardButton("🏆 Top Music Lovers", callback_data="top_users")], 
        [InlineKeyboardButton("⏹ Close", callback_data="close_profile")]
    ])
    await cq.message.edit_text(
    "🎶 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗟𝗲𝗮𝗱𝗲𝗿𝗯𝗼𝗮𝗿𝗱! 📊\n\n"
    "Discover the top-performing groups and users based on their song plays!\n\n"
    "Select a category below to view:",
    reply_markup=kb
)
