import os
import re
import random
import aiohttp
import aiofiles
import traceback

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch


def changeImageSize(maxWidth, maxHeight, image):
    ratio = min(maxWidth / image.size[0], maxHeight / image.size[1])
    newSize = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    return image.resize(newSize, Image.ANTIALIAS)


def truncate(text, max_chars=50):
    words = text.split()
    text1, text2 = "", ""
    for word in words:
        if len(text1 + " " + word) <= max_chars and not text2:
            text1 += " " + word
        else:
            text2 += " " + word
    return [text1.strip(), text2.strip()]


def fit_text(draw, text, max_width, font_path, start_size, min_size):
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)


def rounded_square(size, radius, color):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), size], radius, fill=color)
    return image


async def get_thumb(videoid: str):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
            duration = result.get("duration", "Unknown Mins")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        player = Image.open("ChampuMusic/assets/player.png")
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        # Create background with player overlay
        background = image2.copy()
        background.paste(player, (0, 0), player)

        # Create rounded square logo positioned slightly left of center
        Xcenter = image2.width / 2 - 150  # Shift left by 150 pixels
        Ycenter = image2.height / 2
        logo_size = 340
        logo = youtube.crop((Xcenter - logo_size//2, Ycenter - logo_size//2, 
                            Xcenter + logo_size//2, Ycenter + logo_size//2))
        logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)
        
        # Create rounded square mask
        mask = rounded_square((logo_size, logo_size), 30, (255, 255, 255))
        
        # Apply rounded corners to logo
        logo.putalpha(mask.split()[3])
        
        # Add border to logo
        rand = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        logo_with_border = ImageOps.expand(logo, border=10, fill=rand)
        
        # Position logo on background
        logo_pos = (int(Xcenter - logo_size//2 - 10), int(Ycenter - logo_size//2 - 10))
        background.paste(logo_with_border, logo_pos, logo_with_border)

        draw = ImageDraw.Draw(background)
        font_info = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 22)
        font_time = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 20)
        font_path = "ChampuMusic/assets/font3.ttf"

        # Position text to the right of the logo
        text_x = int(Xcenter + logo_size//2 + 30)
        title_max_width = background.width - text_x - 30

        title_lines = truncate(title, 30)
        title_font1 = fit_text(draw, title_lines[0], title_max_width, font_path, 32, 22)
        draw.text((text_x, int(Ycenter - 80)), title_lines[0], (255, 255, 255), font=title_font1)

        if title_lines[1]:
            title_font2 = fit_text(draw, title_lines[1], title_max_width, font_path, 28, 18)
            draw.text((text_x, int(Ycenter - 40)), title_lines[1], (220, 220, 220), font=title_font2)

        draw.text((text_x, int(Ycenter + 10)), f"{channel} | {views}", (240, 240, 240), font=font_info)

        # Add watermark
        watermark_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 20)
        watermark_text = "@ShivanshuHUB"
        text_size = draw.textsize(watermark_text, font=watermark_font)
        x = background.width - text_size[0] - 20
        y = background.height - text_size[1] - 20
        draw.text((x, y), watermark_text, (255, 255, 255, 200), font=watermark_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except:
        traceback.print_exc()
        return None