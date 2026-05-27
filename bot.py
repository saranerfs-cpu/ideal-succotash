import asyncio
from datetime import datetime
from aiogram import Bot
import requests

# ============================================
# ДАННЫЕ
# ============================================

BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"

CHAT_ID = "5296078628"

TIKTOK_USERNAME = "stxz.ed1ts"

# ============================================
# БОТ
# ============================================

bot = Bot(token=BOT_TOKEN)

# ============================================
# ПАМЯТЬ
# ============================================

old_videos = {}

# ============================================
# ЭМОДЗИ
# ============================================

LIKE = "❤️"
COMMENT = "💬"
VIDEO = "🎬"
SHARE = "📤"
FIRE = "🔥"

# ============================================
# ФЕЙКОВЫЕ ДАННЫЕ ВИДЕО
# ============================================

def get_videos():

    return [
        {
            "id": "1",
            "title": "TikTok Video",
            "likes": 100,
            "comments": 5,
            "shares": 2,
            "url": f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/1"
        }
    ]

# ============================================
# ОТПРАВКА
# ============================================

async def send_message(video, event):

    text = f"""
{FIRE} <b>TikTok Monitor</b>

{event}

🎥 <b>{video['title']}</b>

❤️ Лайки: <b>{video['likes']}</b>
💬 Комменты: <b>{video['comments']}</b>
📤 Репосты: <b>{video['shares']}</b>

🔗 {video['url']}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    await bot.send_message(
        CHAT_ID,
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ============================================
# МОНИТОР
# ============================================

async def monitor():

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

                    await send_message(
                        video,
                        f"{VIDEO} <b>Новое видео!</b>"
                    )

                else:

                    old = old_videos[video_id]

                    if video["likes"] > old["likes"]:

                        await send_message(
                            video,
                            f"{LIKE} <b>Новые лайки!</b>"
                        )

                        old["likes"] = video["likes"]

                    if video["comments"] > old["comments"]:

                        await send_message(
                            video,
                            f"{COMMENT} <b>Новый комментарий!</b>"
                        )

                        old["comments"] = video["comments"]

                    if video["shares"] > old["shares"]:

                        await send_message(
                            video,
                            f"{SHARE} <b>Новый репост!</b>"
                        )

                        old["shares"] = video["shares"]

            await asyncio.sleep(60)

        except Exception as e:

            print(e)

            await asyncio.sleep(10)

# ============================================
# СТАРТ
# ============================================

async def main():

    await bot.send_message(
        CHAT_ID,
        f"{FIRE} Бот запущен!"
    )

    await monitor()

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    asyncio.run(main())
