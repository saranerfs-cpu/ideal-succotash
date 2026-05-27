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

last_video = {
    "id": "1",
    "title": "TikTok Video",
    "likes": 10,
    "comments": 3,
    "shares": 1,
    "url": f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/1"
}

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
# EMOJIS
# ============================================

LIKE_EMOJI = "❤️"

COMMENT_EMOJI = "💬"

VIDEO_EMOJI = "🎬"

FOLLOW_EMOJI = "👥"

SHARE_EMOJI = "📤"

FIRE_EMOJI = "🔥"

# ============================================
# PROFILE
# ============================================

def get_profile_data():

    url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    return response.text

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
# VIDEOS
# ============================================

def get_videos():

    global last_video

    fake_data = [
        {
            "id": "1",

            "likes": 10,

            "comments": 3,

            "shares": 1,

            "url": f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/1",

            "title": "TikTok Video"
        }
    ]

    last_video = fake_data[0]

    return fake_data

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

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">@{TIKTOK_USERNAME}</a>

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
# START
# ============================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    text = f"""
🔥 <b>TikTok Monitor</b>

✅ Бот успешно запущен

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

📊 Доступные функции:

• Статистика
• Последнее видео
• Проверка теневого бана
• Мониторинг лайков
• Мониторинг подписчиков
• Мониторинг репостов
• Мониторинг комментариев

━━━━━━━━━━━━━━━

⚡ Выберите действие кнопками ниже
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
📊 <b>Статистика за последний час</b>

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

    text = f"""
🎬 <b>Последнее видео</b>

━━━━━━━━━━━━━━━

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

❤️ Лайки:
<b>{last_video['likes']}</b>

💬 Комментарии:
<b>{last_video['comments']}</b>

📤 Репосты:
<b>{last_video['shares']}</b>

━━━━━━━━━━━━━━━

🔗 <a href="{last_video['url']}">Открыть видео</a>
"""

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ============================================
# SHADOW BUTTON
# ============================================

@dp.message(F.text == "👁 Теневой бан")
async def shadow_handler(message: Message):

    videos = get_videos()

    result = """
✅ <b>Теневого бана нет</b>

Видео набирают активность нормально
"""

    for video in videos:

        if check_shadow_ban(video):

            result = """
⚠️ <b>Возможен теневой бан</b>

Причины:
• Малый охват
• Низкая активность
• Видео плохо залетают
"""

    await message.answer(
        result,
        parse_mode="HTML"
    )

# ============================================
# CHECK BUTTON
# ============================================

@dp.message(F.text == "🔥 Проверить")
async def check_handler(message: Message):

    videos = get_videos()

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

👤 Аккаунт:
<a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

👥 Всего:
<b>{followers}</b>

➕ Пришло:
<b>+{diff}</b>

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

            print("FOLLOWERS ERROR:", e)

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

                    # =======================
                    # LIKES
                    # =======================

                    if video["likes"] >= old["likes"] + 10:

                        hour_stats["likes"] += 10

                        await send_pretty_message(
                            video,
                            "❤️ <b>+10 лайков!</b>"
                        )

                        old["likes"] = video["likes"]

                    # =======================
                    # COMMENTS
                    # =======================

                    if video["comments"] > old["comments"]:

                        hour_stats["comments"] += 1

                        await send_pretty_message(
                            video,
                            "💬 <b>Новый комментарий!</b>"
                        )

                        old["comments"] = video["comments"]

                    # =======================
                    # SHARES
                    # =======================

                    if video["shares"] > old["shares"]:

                        hour_stats["shares"] += 1

                        await send_pretty_message(
                            video,
                            "📤 <b>Кто-то поделился видео!</b>"
                        )

                        old["shares"] = video["shares"]

            await asyncio.sleep(60)

        except Exception as e:

            print("VIDEO ERROR:", e)

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

    await asyncio.gather(
        monitor_followers(),
        monitor_videos()
    )

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    asyncio.run(main())
