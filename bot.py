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

# =====================================================
# TELEGRAM
# =====================================================

TELEGRAM_BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"

CHAT_ID = "5296078628"

# =====================================================
# TIKTOK
# =====================================================

TIKTOK_USERNAME = "stxz.ed1ts"

CLIENT_KEY = "aws9c59qtbjw446y"

CLIENT_SECRET = "rriXqmqBtgQUkDcD3uzuuBEUikxxa0NT"

# =====================================================
# BOT
# =====================================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher()

# =====================================================
# MEMORY
# =====================================================

old_followers = 0

old_video = {}

stats_30min = {
    "likes": 0,
    "views": 0,
    "comments": 0,
    "shares": 0,
    "followers": 0
}

# =====================================================
# BUTTONS
# =====================================================

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

# =====================================================
# GET HTML
# =====================================================

def get_html():

    try:

        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        return response.text

    except Exception as e:

        print("HTML ERROR:", e)

        return ""

# =====================================================
# FOLLOWERS
# =====================================================

def get_followers():

    try:

        html = get_html()

        match = re.search(
            r'"followerCount":(\d+)',
            html
        )

        if match:

            return int(match.group(1))

    except Exception as e:

        print("FOLLOWERS ERROR:", e)

    return 0

# =====================================================
# LAST VIDEO
# =====================================================

def get_last_video():

    try:

        html = get_html()

        # =========================================
        # VIDEO ID
        # =========================================

        id_match = re.search(
            r'"id":"(\d+)"',
            html
        )

        # =========================================
        # TITLE
        # =========================================

        title_match = re.search(
            r'"desc":"(.*?)"',
            html
        )

        # =========================================
        # LIKES
        # =========================================

        likes_match = re.search(
            r'"diggCount":(\d+)',
            html
        )

        # =========================================
        # COMMENTS
        # =========================================

        comments_match = re.search(
            r'"commentCount":(\d+)',
            html
        )

        # =========================================
        # SHARES
        # =========================================

        shares_match = re.search(
            r'"shareCount":(\d+)',
            html
        )

        # =========================================
        # VIEWS
        # =========================================

        views_match = re.search(
            r'"playCount":(\d+)',
            html
        )

        video_id = (
            id_match.group(1)
            if id_match else "0"
        )

        title = (
            title_match.group(1)
            if title_match else "TikTok Video"
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

        views = (
            int(views_match.group(1))
            if views_match else 0
        )

        video_url = (
            f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{video_id}"
        )

        return {
            "id": video_id,
            "title": title,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "url": video_url
        }

    except Exception as e:

        print("VIDEO ERROR:", e)

        return None

# =====================================================
# SHADOW BAN
# =====================================================

def shadow_ban_check(video):

    try:

        followers = get_followers()

        if followers == 0:

            return "❌ Нет данных"

        views = video["views"]

        likes = video["likes"]

        reach = (
            views / followers
        ) * 100

        engagement = (
            likes / max(views, 1)
        ) * 100

        if reach < 5:

            return """
⚠️ Возможен теневой бан

• Очень маленький охват
• Видео не попадают в рекомендации
"""

        if engagement < 1:

            return """
⚠️ Возможен теневой бан

• Очень низкая активность
"""

        return """
✅ Теневого бана нет

Видео получают нормальный охват
"""

    except Exception as e:

        print("SHADOW ERROR:", e)

        return "❌ Ошибка проверки"

# =====================================================
# BEAUTIFUL MESSAGE
# =====================================================

async def send_message(title, text):

    final_text = f"""
🔥 <b>{title}</b>

{text}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    await bot.send_message(
        CHAT_ID,
        final_text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# =====================================================
# START
# =====================================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    video = get_last_video()

    if not video:

        await message.answer(
            "❌ Не удалось получить видео"
        )

        return

    followers = get_followers()

    text = f"""
👋 <b>TikTok Monitor</b>

👤 <a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

👥 Подписчики:
<b>{followers}</b>

━━━━━━━━━━━━━━━

🎬 Последнее видео

❤️ {video['likes']}
💬 {video['comments']}
📤 {video['shares']}
👁 {video['views']}

━━━━━━━━━━━━━━━

🔗 <a href="{video['url']}">
Открыть видео
</a>
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_web_page_preview=False
    )

# =====================================================
# STATS
# =====================================================

@dp.message(F.text == "📊 Статистика")
async def stats_handler(message: Message):

    followers = get_followers()

    text = f"""
📊 <b>Статистика за 30 минут</b>

━━━━━━━━━━━━━━━

❤️ Лайки:
<b>+{stats_30min['likes']}</b>

👁 Просмотры:
<b>+{stats_30min['views']}</b>

💬 Комментарии:
<b>+{stats_30min['comments']}</b>

📤 Репосты:
<b>+{stats_30min['shares']}</b>

👥 Подписчики:
<b>+{stats_30min['followers']}</b>

━━━━━━━━━━━━━━━

👤 Всего подписчиков:
<b>{followers}</b>
"""

    await message.answer(
        text,
        parse_mode="HTML"
    )

# =====================================================
# LAST VIDEO BUTTON
# =====================================================

@dp.message(F.text == "🎬 Последнее видео")
async def last_video_handler(message: Message):

    video = get_last_video()

    if not video:

        await message.answer(
            "❌ Видео не найдено"
        )

        return

    text = f"""
🎬 <b>Последнее видео</b>

━━━━━━━━━━━━━━━

❤️ {video['likes']}
💬 {video['comments']}
📤 {video['shares']}
👁 {video['views']}

━━━━━━━━━━━━━━━

🔗 <a href="{video['url']}">
Открыть видео
</a>
"""

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# =====================================================
# SHADOW BUTTON
# =====================================================

@dp.message(F.text == "👁 Теневой бан")
async def shadow_handler(message: Message):

    video = get_last_video()

    result = shadow_ban_check(video)

    await message.answer(
        result,
        parse_mode="HTML"
    )

# =====================================================
# CHECK BUTTON
# =====================================================

@dp.message(F.text == "🔥 Проверить")
async def check_handler(message: Message):

    video = get_last_video()

    if not video:

        await message.answer(
            "❌ Нет данных"
        )

        return

    text = f"""
🔥 <b>Проверка завершена</b>

━━━━━━━━━━━━━━━

🎬 <b>{video['title']}</b>

❤️ {video['likes']}
💬 {video['comments']}
📤 {video['shares']}
👁 {video['views']}

━━━━━━━━━━━━━━━

🔗 <a href="{video['url']}">
Открыть видео
</a>
"""

    await message.answer(
        text,
        parse_mode="HTML"
    )

# =====================================================
# MONITOR FOLLOWERS
# =====================================================

async def monitor_followers():

    global old_followers

    while True:

        try:

            followers = get_followers()

            if old_followers == 0:

                old_followers = followers

            if followers > old_followers:

                diff = followers - old_followers

                stats_30min["followers"] += diff

                await send_message(
                    "👥 Новый подписчик",
                    f"""
➕ Новых:
<b>+{diff}</b>

👤 Всего:
<b>{followers}</b>
"""
                )

                old_followers = followers

        except Exception as e:

            print("FOLLOWERS MONITOR ERROR:", e)

        await asyncio.sleep(60)

# =====================================================
# MONITOR VIDEO
# =====================================================

async def monitor_video():

    global old_video

    while True:

        try:

            video = get_last_video()

            if not video:

                await asyncio.sleep(60)

                continue

            # =====================================
            # NEW VIDEO
            # =====================================

            if old_video == {}:

                old_video = video

            elif video["id"] != old_video["id"]:

                await send_message(
                    "🎬 Выложено новое видео",
                    f"""
❤️ {video['likes']}
💬 {video['comments']}
📤 {video['shares']}
👁 {video['views']}

🔗 <a href="{video['url']}">
Открыть видео
</a>
"""
                )

                old_video = video

            else:

                # =================================
                # LIKES
                # =================================

                if video["likes"] > old_video["likes"]:

                    diff = (
                        video["likes"]
                        - old_video["likes"]
                    )

                    stats_30min["likes"] += diff

                    await send_message(
                        "❤️ Новые лайки",
                        f"""
➕ Лайков:
<b>+{diff}</b>
"""
                    )

                    old_video["likes"] = video["likes"]

                # =================================
                # COMMENTS
                # =================================

                if video["comments"] > old_video["comments"]:

                    diff = (
                        video["comments"]
                        - old_video["comments"]
                    )

                    stats_30min["comments"] += diff

                    await send_message(
                        "💬 Новый комментарий",
                        f"""
➕ Комментариев:
<b>+{diff}</b>

🎬 На последнем видео
"""
                    )

                    old_video["comments"] = video["comments"]

                # =================================
                # SHARES
                # =================================

                if video["shares"] > old_video["shares"]:

                    diff = (
                        video["shares"]
                        - old_video["shares"]
                    )

                    stats_30min["shares"] += diff

                    await send_message(
                        "📤 Новый репост",
                        f"""
➕ Репостов:
<b>+{diff}</b>
"""
                    )

                    old_video["shares"] = video["shares"]

                # =================================
                # VIEWS
                # =================================

                if video["views"] > old_video["views"]:

                    diff = (
                        video["views"]
                        - old_video["views"]
                    )

                    stats_30min["views"] += diff

                    old_video["views"] = video["views"]

        except Exception as e:

            print("VIDEO MONITOR ERROR:", e)

        await asyncio.sleep(60)

# =====================================================
# RESET STATS
# =====================================================

async def reset_stats():

    while True:

        await asyncio.sleep(1800)

        stats_30min["likes"] = 0
        stats_30min["views"] = 0
        stats_30min["comments"] = 0
        stats_30min["shares"] = 0
        stats_30min["followers"] = 0

# =====================================================
# WEB SERVER
# =====================================================

async def home(request):

    return web.Response(
        text="TikTok Monitor Running"
    )

async def start_web():

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

# =====================================================
# MAIN
# =====================================================

async def main():

    print("BOT STARTED")

    await start_web()

    await bot.send_message(
        CHAT_ID,
        "🔥 TikTok Monitor запущен!"
    )

    asyncio.create_task(
        dp.start_polling(bot)
    )

    await asyncio.gather(
        monitor_followers(),
        monitor_video(),
        reset_stats()
    )

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
