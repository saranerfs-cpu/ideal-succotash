import asyncio
import requests
import re
import os

from datetime import datetime

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# ============================================
# TELEGRAM
# ============================================

TELEGRAM_BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"

CHAT_ID = "5296078628"

# ============================================
# TIKTOK
# ============================================

TIKTOK_USERNAME = "stxz.ed1ts"

CLIENT_KEY = "aws9c59qtbjw446y"

CLIENT_SECRET = "rriXqmqBtgQUkDcD3uzuuBEUikxxa0NT"

# ============================================
# BOT
# ============================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher()

# ============================================
# MEMORY
# ============================================

old_videos = {}

old_followers = 0

last_video = {}

hour_stats = {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "followers": 0
}

# ============================================
# BUTTONS
# ============================================

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Статистика")
        ],
        [
            KeyboardButton(text="🎬 Последнее видео")
        ],
        [
            KeyboardButton(text="👁 Теневой бан")
        ],
        [
            KeyboardButton(text="🔥 Проверить")
        ]
    ],
    resize_keyboard=True
)

# ============================================
# PROFILE DATA
# ============================================

def get_profile_data():

    try:

        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers
        )

        return response.text

    except Exception as e:

        print("PROFILE ERROR:", e)

        return ""

# ============================================
# FOLLOWERS
# ============================================

def get_followers():

    try:

        html = get_profile_data()

        match = re.search(
            r'"followerCount":(\d+)',
            html
        )

        if match:

            return int(match.group(1))

    except Exception as e:

        print("FOLLOWERS ERROR:", e)

    return 0

# ============================================
# REAL TIKTOK VIDEOS
# ============================================

def get_videos():

    global last_video

    try:

        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers
        )

        html = response.text

        # ====================================
        # VIDEO ID
        # ====================================

        video_id_match = re.search(
            r'"id":"(\d+)"',
            html
        )

        # ====================================
        # LIKES
        # ====================================

        likes_match = re.search(
            r'"diggCount":(\d+)',
            html
        )

        # ====================================
        # COMMENTS
        # ====================================

        comments_match = re.search(
            r'"commentCount":(\d+)',
            html
        )

        # ====================================
        # SHARES
        # ====================================

        shares_match = re.search(
            r'"shareCount":(\d+)',
            html
        )

        # ====================================
        # TITLE
        # ====================================

        title_match = re.search(
            r'"desc":"(.*?)"',
            html
        )

        # ====================================
        # VALUES
        # ====================================

        video_id = (
            video_id_match.group(1)
            if video_id_match else "0"
        )

        likes = (
            int(likes_match.group(1))
            if likes_match else 0
        )

        comments = (
            int(comments_match.group(1))
            if comments_match else 0
        )

        shares = (
            int(shares_match.group(1))
            if shares_match else 0
        )

        title = (
            title_match.group(1)
            if title_match else "TikTok Video"
        )

        video_url = (
            f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{video_id}"
        )

        video_data = {
            "id": video_id,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "url": video_url,
            "title": title
        }

        last_video = video_data

        return [video_data]

    except Exception as e:

        print("VIDEOS ERROR:", e)

        return []

# ============================================
# SHADOW BAN
# ============================================

def check_shadow_ban(video):

    estimated_views = video["likes"] * 10

    if estimated_views < 100:

        return True

    return False

# ============================================
# BEAUTIFUL MESSAGE
# ============================================

async def send_pretty_message(
    video,
    event_type,
    extra_text=""
):

    text = f"""
🔥 <b>TikTok Monitor</b>

{event_type}

━━━━━━━━━━━━━━━

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

🎬 <b>{video['title']}</b>

❤️ Лайки:
<b>{video['likes']}</b>

💬 Комментарии:
<b>{video['comments']}</b>

📤 Репосты:
<b>{video['shares']}</b>

━━━━━━━━━━━━━━━

🔗 <a href="{video['url']}">Открыть видео</a>

{extra_text}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    await bot.send_message(
        CHAT_ID,
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ============================================
# START COMMAND
# ============================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    text = f"""
🔥 <b>TikTok Monitor запущен</b>

━━━━━━━━━━━━━━━

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

✅ Мониторинг лайков

✅ Мониторинг комментариев

✅ Мониторинг репостов

✅ Мониторинг подписчиков

✅ Проверка теневого бана

━━━━━━━━━━━━━━━

⚡ Используй кнопки ниже
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# ============================================
# STATS BUTTON
# ============================================

@dp.message(F.text == "📊 Статистика")
async def stats_handler(message: Message):

    followers = get_followers()

    text = f"""
📊 <b>Статистика</b>

━━━━━━━━━━━━━━━

❤️ Лайки:
<b>{hour_stats['likes']}</b>

💬 Комментарии:
<b>{hour_stats['comments']}</b>

📤 Репосты:
<b>{hour_stats['shares']}</b>

👥 Подписчики:
<b>{hour_stats['followers']}</b>

━━━━━━━━━━━━━━━

👤 Всего подписчиков:
<b>{followers}</b>
"""

    await message.answer(
        text,
        parse_mode="HTML"
    )

# ============================================
# LAST VIDEO BUTTON
# ============================================

@dp.message(F.text == "🎬 Последнее видео")
async def last_video_handler(message: Message):

    videos = get_videos()

    if not videos:

        await message.answer(
            "❌ Видео не найдено"
        )

        return

    video = videos[0]

    text = f"""
🎬 <b>Последнее видео</b>

━━━━━━━━━━━━━━━

🎥 <b>{video['title']}</b>

❤️ Лайки:
<b>{video['likes']}</b>

💬 Комментарии:
<b>{video['comments']}</b>

📤 Репосты:
<b>{video['shares']}</b>

━━━━━━━━━━━━━━━

🔗 <a href="{video['url']}">Открыть видео</a>
"""

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ============================================
# SHADOW BAN BUTTON
# ============================================

@dp.message(F.text == "👁 Теневой бан")
async def shadow_handler(message: Message):

    videos = get_videos()

    if not videos:

        await message.answer(
            "❌ Не удалось проверить"
        )

        return

    video = videos[0]

    if check_shadow_ban(video):

        text = """
⚠️ <b>Возможен теневой бан</b>

• Низкая активность
• Малый охват
• Видео плохо залетают
"""

    else:

        text = """
✅ <b>Теневого бана нет</b>

Видео набирают активность нормально
"""

    await message.answer(
        text,
        parse_mode="HTML"
    )

# ============================================
# CHECK BUTTON
# ============================================

@dp.message(F.text == "🔥 Проверить")
async def check_handler(message: Message):

    videos = get_videos()

    if not videos:

        await message.answer(
            "❌ Не удалось получить видео"
        )

        return

    for video in videos:

        await send_pretty_message(
            video,
            "🔥 <b>Ручная проверка</b>"
        )

# ============================================
# FOLLOWERS MONITOR
# ============================================

async def monitor_followers():

    global old_followers

    while True:

        try:

            followers = get_followers()

            if old_followers == 0:

                old_followers = followers

            if followers > old_followers:

                diff = followers - old_followers

                hour_stats["followers"] += diff

                text = f"""
👥 <b>Новые подписчики!</b>

━━━━━━━━━━━━━━━

➕ Пришло:
<b>+{diff}</b>

👤 Всего:
<b>{followers}</b>

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

                await bot.send_message(
                    CHAT_ID,
                    text,
                    parse_mode="HTML"
                )

                old_followers = followers

            print("FOLLOWERS:", followers)

        except Exception as e:

            print("FOLLOWERS MONITOR ERROR:", e)

        await asyncio.sleep(60)

# ============================================
# VIDEO MONITOR
# ============================================

async def monitor_videos():

    global old_videos

    while True:

        try:

            videos = get_videos()

            for video in videos:

                video_id = video["id"]

                if video_id not in old_videos:

                    old_videos[video_id] = {
                        "likes": video["likes"],
                        "comments": video["comments"],
                        "shares": video["shares"]
                    }

                    await send_pretty_message(
                        video,
                        "🎬 <b>Новое видео опубликовано!</b>"
                    )

                else:

                    old = old_videos[video_id]

                    # ============================
                    # LIKES
                    # ============================

                    if video["likes"] > old["likes"]:

                        diff = video["likes"] - old["likes"]

                        hour_stats["likes"] += diff

                        await send_pretty_message(
                            video,
                            f"❤️ <b>+{diff} лайков!</b>"
                        )

                        old["likes"] = video["likes"]

                    # ============================
                    # COMMENTS
                    # ============================

                    if video["comments"] > old["comments"]:

                        diff = (
                            video["comments"]
                            - old["comments"]
                        )

                        hour_stats["comments"] += diff

                        await send_pretty_message(
                            video,
                            f"💬 <b>+{diff} комментариев!</b>"
                        )

                        old["comments"] = video["comments"]

                    # ============================
                    # SHARES
                    # ============================

                    if video["shares"] > old["shares"]:

                        diff = (
                            video["shares"]
                            - old["shares"]
                        )

                        hour_stats["shares"] += diff

                        await send_pretty_message(
                            video,
                            f"📤 <b>+{diff} репостов!</b>"
                        )

                        old["shares"] = video["shares"]

            await asyncio.sleep(60)

        except Exception as e:

            print("VIDEO MONITOR ERROR:", e)

            await asyncio.sleep(10)

# ============================================
# WEB SERVER
# ============================================

async def home(request):

    return web.Response(
        text="TikTok Monitor Running"
    )

async def start_webserver():

    app = web.Application()

    app.router.add_get("/", home)

    port = int(
        os.environ.get("PORT", 10000)
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(f"WEB SERVER STARTED {port}")

# ============================================
# MAIN
# ============================================

async def main():

    print("BOT STARTED")

    await start_webserver()

    await bot.send_message(
        CHAT_ID,
        "🔥 TikTok Monitor успешно запущен!"
    )

    asyncio.create_task(
        dp.start_polling(bot)
    )

    await asyncio.gather(
        monitor_followers(),
        monitor_videos()
    )

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    asyncio.run(main())
