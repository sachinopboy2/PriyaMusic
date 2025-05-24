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

        # Load and prepare background
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        gradient = Image.new("RGBA", image2.size, (0, 0, 0, 255))
        enhancer = ImageEnhance.Brightness(image2.filter(ImageFilter.GaussianBlur(15)))
        blurred = enhancer.enhance(0.5)
        background = Image.alpha_composite(gradient, blurred)

        draw = ImageDraw.Draw(background)
        font_info = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 24)
        font_path = "ChampuMusic/assets/font3.ttf"

        # === Full-screen Player Overlay ===
        player = Image.open("ChampuMusic/assets/player.png").convert("RGBA")
        player = player.resize((1280, 720))
        background.paste(player, (0, 0), player)

        # === Album Art Thumbnail (Larger, Rounded, Centered Vertically) ===
        thumb_size = 300
        thumb_x = 40
        thumb_y = (720 - thumb_size) // 2
        
        # Create rounded corners mask
        mask = Image.new('L', (thumb_size, thumb_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0, 0), (thumb_size, thumb_size)], radius=30, fill=255)
        
        # Resize and apply rounded corners
        thumb_square = youtube.resize((thumb_size, thumb_size))
        thumb_square.putalpha(mask)
        
        # Paste the rounded thumbnail
        background.paste(thumb_square, (thumb_x, thumb_y), thumb_square)

        # === User Profile Photo ===
        profile_size = 80
        profile_x = thumb_x + thumb_size + 30
        profile_y = thumb_y + thumb_size - profile_size  # Align bottom with album art
        
        # Determine which profile image to use (user > group > bot)
        profile_url = None
        if user_photo_url:
            profile_url = user_photo_url
        elif group_photo_url:
            profile_url = group_photo_url
        elif bot_photo_url:
            profile_url = bot_photo_url
            
        if profile_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(profile_url) as resp:
                        if resp.status == 200:
                            profile_data = await resp.read()
                            f = await aiofiles.open(f"cache/profile{videoid}.png", mode="wb")
                            await f.write(profile_data)
                            await f.close()
                            
                            profile_img = Image.open(f"cache/profile{videoid}.png").convert("RGBA")
                            # Make circular mask
                            mask = Image.new('L', (profile_size, profile_size), 0)
                            draw_mask = ImageDraw.Draw(mask)
                            draw_mask.ellipse((0, 0, profile_size, profile_size), fill=255)
                            
                            profile_img = profile_img.resize((profile_size, profile_size))
                            profile_img.putalpha(mask)
                            background.paste(profile_img, (profile_x, profile_y), profile_img)
                            os.remove(f"cache/profile{videoid}.png")
            except:
                traceback.print_exc()
                # If profile image fails, we'll just continue without it

        # === Title and Channel Info ===
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

        # === Watermark ===
        watermark_font = ImageFont.truetype("ChampuMusic/assets/font2.ttf", 24)
        watermark_text = "@ShivanshuHUB"
        text_size = draw.textsize(watermark_text, font=watermark_font)
        x = background.width - text_size[0] - 25
        y = background.height - text_size[1] - 25
        glow_pos = [(x + dx, y + dy) for dx in (-1, 1) for dy in (-1, 1)]
        for pos in glow_pos:
            draw.text(pos, watermark_text, font=watermark_font, fill=(0, 0, 0, 180))
        draw.text((x, y), watermark_text, font=watermark_font, fill=(255, 255, 255, 240))

        # === Save Final Output ===
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