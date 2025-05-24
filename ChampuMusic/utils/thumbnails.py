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


async def get_thumb(videoid: str, user_photo_url: str = None, group_photo_url: str = None, bot_photo_url: str = None):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Download YouTube thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube).convert("RGBA")

        gradient = Image.new("RGBA", image1.size, (0, 0, 0, 255))
        enhancer = ImageEnhance.Brightness(image1.filter(ImageFilter.GaussianBlur(15)))
        blurred = enhancer.enhance(0.5)
        background = Image.alpha_composite(gradient, blurred)

        draw = ImageDraw.Draw(background)
        font_info = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 24)
        font_path = "ChampuMusic/assets/font3.ttf"

        # Overlay player
        player = Image.open("ChampuMusic/assets/player.png").convert("RGBA").resize((1280, 720))
        background.paste(player, (0, 0), player)

        # Album Art
        thumb_size = 300
        thumb_x = 40
        thumb_y = (720 - thumb_size) // 2

        mask = Image.new('L', (thumb_size, thumb_size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (thumb_size, thumb_size)], radius=30, fill=255)

        thumb_square = youtube.resize((thumb_size, thumb_size))
        thumb_square.putalpha(mask)
        background.paste(thumb_square, (thumb_x, thumb_y), thumb_square)

        # === Determine Profile Image ===
        profile_url = user_photo_url or group_photo_url or bot_photo_url
        profile_size = 80
        profile_x = thumb_x + thumb_size + 30
        profile_y = thumb_y + thumb_size - profile_size

        if profile_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(profile_url) as resp:
                        if resp.status == 200:
                            profile_data = await resp.read()
                            profile_path = f"cache/profile{videoid}.png"
                            async with aiofiles.open(profile_path, mode="wb") as f:
                                await f.write(profile_data)

                            profile_img = Image.open(profile_path).convert("RGBA").resize((profile_size, profile_size))
                            mask = Image.new('L', (profile_size, profile_size), 0)
                            ImageDraw.Draw(mask).ellipse((0, 0, profile_size, profile_size), fill=255)
                            profile_img.putalpha(mask)
                            background.paste(profile_img, (profile_x, profile_y), profile_img)
                            os.remove(profile_path)
            except Exception as e:
                print(f"[Profile Image Error] {e}")
                traceback.print_exc()

        # Title and Channel Info
        text_x = profile_x + profile_size + 20 if profile_url else thumb_x + thumb_size + 20
        title_y = thumb_y + 20
        info_y = title_y + 40

        def truncate_text(text, max_chars=40):
            return (text[:max_chars - 3] + "...") if len(text) > max_chars else text

        short_title = truncate_text(title, max_chars=30)
        short_channel = truncate_text(channel, max_chars=30)

        title_font = fit_text(draw, short_title, 600, font_path, 30, 20)
        draw.text((text_x, title_y), short_title, (255, 255, 255), font=title_font)

        info_text = f"{short_channel} • {views}"
        info_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 18)
        draw.text((text_x, info_y), info_text, (200, 200, 200), font=info_font)

        # Watermark
        watermark_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 24)
        watermark_text = "@ShivanshuHUB"
        text_size = draw.textsize(watermark_text, font=watermark_font)
        x = background.width - text_size[0] - 25
        y = background.height - text_size[1] - 25
        for dx in (-1, 1):
            for dy in (-1, 1):
                draw.text((x + dx, y + dy), watermark_text, font=watermark_font, fill=(0, 0, 0, 180))
        draw.text((x, y), watermark_text, font=watermark_font, fill=(255, 255, 255, 240))

        # Save and return path
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except Exception as e:
        print(f"[get_thumb Error] {e}")
        traceback.print_exc()
        return None
