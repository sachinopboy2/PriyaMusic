import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")

# Youtube API credentials
# Get this value from https://console.cloud.google.com/apis/credentials
# Create a project and enable youtube data api v3
# Create a new api key and copy it here
API_KEY = "Rf1qda5gyCITj6VbrekzRxmR"

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", None)

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 600))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", None))

# Get this value from @TheChampuBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", 7006524418))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

LOGGERS = "\x4E\x61\x6E\x63\x79\x58\x52\x6F\x62\x6F\x74"  # connect errors api key "Dont change it"

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/TheChampu/TelegramMusicBot",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/akaChampu")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ShivanshuHUB")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv(
    "SPOTIFY_CLIENT_SECRET", None
)


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://envs.sh/JJR.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://graph.org/file/15fde98db07a70beb6f4a.jpg"
)
PLAYLIST_IMG_URL = "https://telegra.ph/file/8ff7a386f161aea9ed5fb.jpg"
STATS_IMG_URL = "https://graph.org/file/2dcb664a9c0ba9d9d80f6.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org/file/b13a16734bab174f58482.jpg"
TELEGRAM_VIDEO_URL = "https://graph.org/file/5938774f48c1f019c73f7.jpg"
STREAM_IMG_URL = "https://graph.org/file/61b2679bd92a3ab646153.jpg"
SOUNCLOUD_IMG_URL = "https://graph.org/file/7aed421dbfbad17f0469f.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/7e177561e54188f35fa03.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://graph.org/file/42739cf35a58f1eda76f0.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://graph.org/file/9553b762fd6a2aaf7ab0a.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://graph.org/file/08b0f34c8012e2e231978.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )