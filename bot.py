import asyncio
import requests
import re
import os

from datetime import datetime

from aiohttp import web

from aiogram import Bot

# ============================================
# TikTok Monitor Bot
# ============================================

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

# ============================================
# MEMORY
# ============================================

old_videos = {}

old_followers = 0

hour_stats = {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "followers": 0
}

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

    # ====================================
    # ТЕСТОВЫЕ ДАННЫЕ
    # ====================================

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
# PRETTY MESSAGE
# ============================================

async def send_pretty_message(
    video,
    event_type,
    extra_text=""
):

    text = f"""
{FIRE_EMOJI} <b>TikTok Monitor</b>

{event_type}

🎥 <b>Видео:</b>
{video['title']}

❤️ Лайки:
<b>{video['likes']}</b>

💬 Комменты:
<b>{video['comments']}</b>

📤 Репосты:
<b>{video['shares']}</b>

🔗 Ссылка:
{video['url']}

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
{FOLLOW_EMOJI} <b>Новые подписчики!</b>

👥 Всего:
<b>{followers}</b>

➕ Пришло:
<b>+{diff}</b>
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

                # ============================
                # NEW VIDEO
                # ============================

                if video_id not in old_videos:

                    old_videos[video_id] = {
                        "likes": video["likes"],
                        "comments": video["comments"],
                        "shares": video["shares"]
                    }

                    await send_pretty_message(
                        video,
                        f"{VIDEO_EMOJI} <b>Новое видео опубликовано!</b>"
                    )

                else:

                    old = old_videos[video_id]

                    # ============================
                    # LIKES
                    # ============================

                    if video["likes"] >= old["likes"] + 10:

                        hour_stats["likes"] += 10

                        await send_pretty_message(
                            video,
                            f"{LIKE_EMOJI} <b>+10 лайков!</b>"
                        )

                        old["likes"] = video["likes"]

                    # ============================
                    # COMMENTS
                    # ============================

                    if video["comments"] > old["comments"]:

                        hour_stats["comments"] += 1

                        await send_pretty_message(
                            video,
                            f"{COMMENT_EMOJI} <b>Новый комментарий!</b>",
                            extra_text="""
👤 Пользователь:
someone

💬 Комментарий:
Очень круто 🔥
"""
                        )

                        old["comments"] = video["comments"]

                    # ============================
                    # SHARES
                    # ============================

                    if video["shares"] > old["shares"]:

                        hour_stats["shares"] += 1

                        await send_pretty_message(
                            video,
                            f"{SHARE_EMOJI} <b>Кто-то поделился видео!</b>"
                        )

                        old["shares"] = video["shares"]

                    # ============================
                    # SHADOW BAN
                    # ============================

                    if check_shadow_ban(video):

                        await bot.send_message(
                            CHAT_ID,
                            """
⚠️ Возможен теневой бан

• Малый охват
• Видео плохо залетает
• Низкие просмотры
"""
                        )

            await asyncio.sleep(60)

        except Exception as e:

            print("VIDEO ERROR:", e)

            await asyncio.sleep(10)

# ============================================
# STATS
# ============================================

async def stats_sender():

    while True:

        try:

            text = f"""
📊 <b>Статистика за час</b>

❤️ Лайки:
<b>{hour_stats['likes']}</b>

💬 Комменты:
<b>{hour_stats['comments']}</b>

📤 Репосты:
<b>{hour_stats['shares']}</b>

👥 Подписчики:
<b>{hour_stats['followers']}</b>
"""

            await bot.send_message(
                CHAT_ID,
                text,
                parse_mode="HTML"
            )

            hour_stats["likes"] = 0
            hour_stats["comments"] = 0
            hour_stats["shares"] = 0
            hour_stats["followers"] = 0

        except Exception as e:

            print("STATS ERROR:", e)

        await asyncio.sleep(3600)

# ============================================
# WEB SERVER
# ============================================

async def home(request):

    return web.Response(
        text="TikTok Monitor Bot Running"
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

    print(f"WEB SERVER STARTED: {port}")

# ============================================
# MAIN
# ============================================

async def main():

    print("BOT STARTED")

    await start_webserver()

    await bot.send_message(
        CHAT_ID,
        f"{FIRE_EMOJI} TikTok Monitor запущен!"
    )

    await asyncio.gather(
        monitor_followers(),
        monitor_videos(),
        stats_sender()
    )

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    asyncio.run(main())
