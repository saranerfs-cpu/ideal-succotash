import asyncio
import requests
import re
import os
import json

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

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

CHAT_ID = "YOUR_CHAT_ID"

# =====================================================
# TIKTOK
# =====================================================

TIKTOK_USERNAME = "stxz.ed1ts"

# =====================================================
# BOT
# =====================================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher()

# =====================================================
# MEMORY
# =====================================================

old_followers = 0

old_video = None

stats_30min = {
    "followers": 0,
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "views": 0
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
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            )
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
# PROFILE INFO
# =====================================================

def get_profile_stats():

    try:

        html = get_html()

        followers_match = re.search(
            r'"followerCount":(\d+)',
            html
        )

        likes_match = re.search(
            r'"heartCount":(\d+)',
            html
        )

        following_match = re.search(
            r'"followingCount":(\d+)',
            html
        )

        followers = (
            int(followers_match.group(1))
            if followers_match else 0
        )

        likes = (
            int(likes_match.group(1))
            if likes_match else 0
        )

        following = (
            int(following_match.group(1))
            if following_match else 0
        )

        return {
            "followers": followers,
            "likes": likes,
            "following": following
        }

    except Exception as e:

        print("PROFILE STATS ERROR:", e)

        return {
            "followers": 0,
            "likes": 0,
            "following": 0
        }

# =====================================================
# LAST VIDEO
# =====================================================

def get_last_video():

    try:

        html = get_html()

        # =========================================
        # VIDEO IDS
        # =========================================

        ids = re.findall(
            r'"video":{"id":"(\d+)"',
            html
        )

        if not ids:

            ids = re.findall(
                r'"id":"(\d+)"',
                html
            )

        video_id = ids[0]

        # =========================================
        # VIDEO URL
        # =========================================

        video_url = (
            f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{video_id}"
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

        # =========================================
        # TITLE
        # =========================================

        title_match = re.search(
            r'"desc":"(.*?)"',
            html
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

        title = (
            title_match.group(1)
            if title_match else "TikTok Video"
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
# SHADOW BAN CHECK
# =====================================================

def check_shadow(video):

    try:

        profile = get_profile_stats()

        followers = profile["followers"]

        views = video["views"]

        if followers == 0:

            return "❌ Нет данных"

        reach = (
            views / followers
        ) * 100

        if reach < 5:

            return """
⚠️ Возможен теневой бан

• Очень маленький охват
• Видео плохо залетают
"""

        return """
✅ Теневого бана нет

Видео набирают просмотры нормально
"""

    except Exception as e:

        print("SHADOW ERROR:", e)

        return "❌ Ошибка проверки"

# =====================================================
# SEND MESSAGE
# =====================================================

async def send_log(title, text):

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

    profile = get_profile_stats()

    video = get_last_video()

    if not video:

        await message.answer(
            "❌ Не удалось получить данные"
        )

        return

    text = f"""
👋 <b>TikTok Monitor</b>

👤 <a href="https://www.tiktok.com/@{TIKTOK_USERNAME}">
@{TIKTOK_USERNAME}
</a>

━━━━━━━━━━━━━━━

👥 Подписчики:
<b>{profile['followers']}</b>

❤️ Всего лайков:
<b>{profile['likes']}</b>

➕ Подписок:
<b>{profile['following']}</b>

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

    profile = get_profile_stats()

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

👥 Всего подписчиков:
<b>{profile['followers']}</b>

❤️ Всего лайков:
<b>{profile['likes']}</b>
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

    if not video:

        await message.answer(
            "❌ Нет данных"
        )

        return

    result = check_shadow(video)

    await message.answer(
        result,
        parse_mode="HTML"
    )

# =====================================================
# CHECK BUTTON
# =====================================================

@dp.message(F.text == "🔥 Проверить")
async def check_handler(message: Message):

    profile = get_profile_stats()

    video = get_last_video()

    if not video:

        await message.answer(
            "❌ Нет данных"
        )

        return

    text = f"""
🔥 <b>Актуальная информация</b>

━━━━━━━━━━━━━━━

👥 Подписчики:
<b>{profile['followers']}</b>

❤️ Всего лайков:
<b>{profile['likes']}</b>

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
        parse_mode="HTML"
    )

# =====================================================
# MONITOR FOLLOWERS
# =====================================================

async def monitor_followers():

    global old_followers

    while True:

        try:

            profile = get_profile_stats()

            followers = profile["followers"]

            if old_followers == 0:

                old_followers = followers

            elif followers > old_followers:

                diff = followers - old_followers

                stats_30min["followers"] += diff

                print("NEW FOLLOWER")

                await send_log(
                    "👥 Новый подписчик",
                    f"""
➕ Подписчиков:
<b>+{diff}</b>

👥 Всего:
<b>{followers}</b>
"""
                )

                old_followers = followers

        except Exception as e:

            print("FOLLOWERS ERROR:", e)

        await asyncio.sleep(10)

# =====================================================
# MONITOR VIDEO
# =====================================================

async def monitor_video():

    global old_video

    while True:

        try:

            video = get_last_video()

            if not video:

                await asyncio.sleep(10)

                continue

            # =====================================
            # FIRST START
            # =====================================

            if old_video is None:

                old_video = video

            # =====================================
            # NEW VIDEO
            # =====================================

            elif video["id"] != old_video["id"]:

                print("NEW VIDEO")

                await send_log(
                    "🎬 Новое видео",
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

                    print("NEW LIKES")

                    await send_log(
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

                    print("NEW COMMENTS")

                    await send_log(
                        "💬 Новый комментарий",
                        f"""
➕ Комментариев:
<b>+{diff}</b>
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

                    print("NEW SHARES")

                    await send_log(
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

        await asyncio.sleep(10)

# =====================================================
# RESET STATS
# =====================================================

async def reset_stats():

    while True:

        await asyncio.sleep(1800)

        stats_30min["followers"] = 0
        stats_30min["likes"] = 0
        stats_30min["comments"] = 0
        stats_30min["shares"] = 0
        stats_30min["views"] = 0

        print("STATS RESET")

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
        "🔥 TikTok Monitor успешно запущен"
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
