import aiohttp
import io
import asyncio
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from youtubesearchpython.__future__ import VideosSearch

# Replace with your fallback image
YOUTUBE_IMG_URL = "https://files.catbox.moe/2f6prl.jpg"

async def fetch_thumbnail(videoid):
    """
    Fetch the thumbnail URL for a given YouTube video ID.
    """
    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
    except Exception:
        return YOUTUBE_IMG_URL

async def download_image(url):
    """
    Download an image from a URL and return it as a PIL Image object.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return Image.open(io.BytesIO(await resp.read())).convert("RGB")
    return None

async def generate_styled_thumbnail(videoid, title, artist, progress_sec, duration_sec, output_path="styled_thumb.jpg"):
    """
    Generate a styled thumbnail with a blurred background, album art, and progress bar.
    """
    # Fetch the thumbnail URL and download the image
    thumb_url = await fetch_thumbnail(videoid)
    base_image = await download_image(thumb_url)
    if base_image is None:
        raise ValueError("Failed to load thumbnail.")

    # Resize and blur background using OpenCV
    cv_img = cv2.cvtColor(np.array(base_image.resize((1280, 720))), cv2.COLOR_RGB2BGR)
    blurred = cv2.GaussianBlur(cv_img, (51, 51), 0)
    bg_img = Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))

    # Create overlay
    overlay = Image.new("RGBA", bg_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Player box
    player_box = [340, 220, 940, 500]
    draw.rounded_rectangle(player_box, radius=40, fill=(0, 0, 0, 190))

    # Album art
    album_art = base_image.resize((150, 150))
    bg_img.paste(album_art, (360, 245))

    # Load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 34)
        font_artist = ImageFont.truetype("arial.ttf", 26)
        font_time = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        raise ValueError("Font files not found. Ensure 'arial.ttf' is available.")

    # Draw text
    draw.text((530, 250), title, font=font_title, fill="white")
    draw.text((530, 295), artist, font=font_artist, fill="#DDDDDD")

    # Progress bar
    bar_x, bar_y = 530, 350
    bar_w = 350
    progress_ratio = min(max(progress_sec / duration_sec, 0), 1)  # Ensure ratio is between 0 and 1
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 8], fill="#444")
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress_ratio), bar_y + 8], fill="#00E676")
    draw.text((bar_x, bar_y + 12), f"{int(progress_sec // 60)}:{int(progress_sec % 60):02d}", font=font_time, fill="white")
    draw.text((bar_x + bar_w - 50, bar_y + 12), f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}", font=font_time, fill="white")

    # Merge and save
    final_image = Image.alpha_composite(bg_img.convert("RGBA"), overlay)
    final_image.save(output_path)
