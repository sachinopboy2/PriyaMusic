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


async def get_thumb(videoid: str):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "00:00")
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
        blurred = enhancer.enhance(0.3)
        background = Image.alpha_composite(gradient, blurred)

        draw = ImageDraw.Draw(background)
        font_info = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 24)
        font_path = "ChampuMusic/assets/font3.ttf"

        # Overlay player
        player = Image.open("ChampuMusic/assets/player.png").convert("RGBA").resize((1280, 720))
        background.paste(player, (0, 0), player)

        # Circular Album Art 
        thumb_size = 260
        thumb_x = (1280 // 2) - (thumb_size // 2) - int(1280 * 0.18)  
        thumb_y = (720 - thumb_size) // 2

        # Create circular mask
        mask = Image.new('L', (thumb_size, thumb_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, thumb_size, thumb_size), fill=255)

        thumb_square = youtube.resize((thumb_size, thumb_size))
        thumb_square.putalpha(mask)
        background.paste(thumb_square, (thumb_x, thumb_y), thumb_square)

        # Title and Channel Info
        text_x = thumb_x + thumb_size + 40  
        title_y = thumb_y + 20  
        info_y = title_y + 60  
        progress_y = info_y + 20  

        def truncate_text(text, max_chars=30):
            return (text[:max_chars - 3] + "...") if len(text) > max_chars else text

        short_title = truncate_text(title, max_chars=20)
        short_channel = truncate_text(channel, max_chars=20)

        title_font = fit_text(draw, short_title, 600, font_path, 40, 25)
        draw.text((text_x, title_y), short_title, (255, 255, 255), font=title_font)

        info_text = f"{short_channel} • {views}"
        info_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 20)  
        draw.text((text_x, info_y), info_text, (200, 200, 200), font=info_font)

        # Progress Bar 
        bar_width = 400
        bar_height = 6
        bar_x = text_x + int(bar_width * 0.01)
        bar_y = info_y + 45  
        
        # Progress bar background
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + bar_width, bar_y + bar_height),
            radius=bar_height//2,
            fill=(100, 100, 100, 200)
        )
        
        # Time indicators
        time_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 20)
        draw.text((bar_x, bar_y + bar_height + 5), "00:00", (200, 200, 200), font=time_font)
        duration_text = duration if ":" in duration else f"00:{duration.zfill(2)}"
        duration_width = draw.textlength(duration_text, font=time_font)
        draw.text((bar_x + bar_width - duration_width, bar_y + bar_height + 5), 
                 duration_text, (200, 200, 200), font=time_font)
        
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