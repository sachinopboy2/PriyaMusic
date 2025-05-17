from ChampuMusic.core.bot import Anony
from ChampuMusic.core.dir import dirr
from ChampuMusic.core.git import git
from ChampuMusic.core.userbot import Userbot
from ChampuMusic.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Anony()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
