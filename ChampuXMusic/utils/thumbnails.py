import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from ChampuXMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    
    
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)
    
    
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    
    return result


async def get_thumb(videoid):
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache", exist_ok=True)

        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        try:
            results = VideosSearch(url, limit=1)
            for result in (await results.next())["result"]:
                title = result.get("title", "Unsupported Title")
                title = re.sub("\W+", " ", title).title()
                duration = result.get("duration", "Unknown Mins")
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                views = result.get("viewCount", {}).get("short", "Unknown Views")
                channel = result.get("channel", {}).get("name", "Unknown Channel")
        except Exception as e:
            print(f"Error fetching video info: {e}")
            return YOUTUBE_IMG_URL

        # Download thumbnail with error handling
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                            await f.write(await resp.read())
                    else:
                        print(f"Thumbnail download failed with status {resp.status}")
                        return YOUTUBE_IMG_URL
        except Exception as e:
            print(f"Thumbnail download error: {e}")
            return YOUTUBE_IMG_URL

        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
        except Exception as e:
            print(f"Error opening thumbnail: {e}")
            return YOUTUBE_IMG_URL

        # Rest of your image processing code...

        return f"cache/{videoid}_v4.png"

    except Exception as e:
        print(f"Error in get_thumb: {e}")
        return YOUTUBE_IMG_URL