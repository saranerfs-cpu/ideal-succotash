import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ==================================================
# ДАННЫЕ
# ==================================================

BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"

CHAT_ID = "5296078628"

TIKTOK_USERNAME = "stxz.ed1ts"

# ==================================================
# BOT
# ==================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ==================================================
# КНОПКИ
# ==================================================

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

keyboard.add(
    KeyboardButton("📊 Статистика")
)

keyboard.add(
    KeyboardButton("👁 Теневой бан")
)

keyboard.add(
    KeyboardButton("🔥 Проверить")
)

# ==================================================
# ПАМЯТЬ
# ==================================================

old_videos = {}

stats = {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "followers": 0
}

# ==================================================
# ЭМОДЗИ
# ==================================================

LIKE = "❤️"
COMMENT = "💬"
VIDEO = "🎬"
SHARE = "📤"
FOLLOW = "👥"
FIRE = "🔥"

# ==================================================
# ПОЛУЧЕНИЕ ВИДЕО
# ==================================================

def get_videos():

    fake_data = [
        {
            "id": "1",
            "title": "TikTok Video",
            "likes": 120,
            "comments": 14,
            "shares": 5,
            "url": f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/1"
        }
    ]

    return fake_data

# ==================================================
# ТЕНЕВОЙ БАН
# ==================================================

def check_shadow(video):

    estimated_views = video["likes"] * 10

    if estimated_views < 100:
        return True

    return False

# ==================================================
# КРАСИВОЕ СООБЩЕНИЕ
# ==================================================

async def send_pretty(video, event, extra=""):

    text = f"""
🔥 <b>TikTok Monitor</b>

{event}

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

{extra}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ==================================================
# СТАТИСТИКА
# ==================================================

@dp.message_handler(text="📊 Статистика")
async def stats_handler(message: types.Message):

    text = f"""
📊 <b>Статистика за час</b>

❤️ Лайки:
<b>{stats['likes']}</b>

💬 Комменты:
<b>{stats['comments']}</b>

📤 Репосты:
<b>{stats['shares']}</b>

👥 Подписчики:
<b>{stats['followers']}</b>
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="HTML"
    )

# ==================================================
# ТЕНЕВОЙ БАН
# ==================================================

@dp.message_handler(text="👁 Теневой бан")
async def shadow_handler(message: types.Message):

    videos = get_videos()

    result = "✅ Теневого бана нет"

    for video in videos:

        if check_shadow(video):

            result = """
⚠️ Возможен теневой бан

• Малый охват
• Видео плохо залетает
• Низкие просмотры
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=result
    )

# ==================================================
# РУЧНАЯ ПРОВЕРКА
# ==================================================

@dp.message_handler(text="🔥 Проверить")
async def manual_check(message: types.Message):

    videos = get_videos()

    for video in videos:

        await send_pretty(
            video,
            "🔥 Ручная проверка"
        )

# ==================================================
# МОНИТОРИНГ
# ==================================================

async def monitor():

    global old_videos

    while True:

        try:

            videos = get_videos()

            for video in videos:

                video_id = video["id"]

                # НОВОЕ ВИДЕО

                if video_id not in old_videos:

                    old_videos[video_id] = {
                        "likes": video["likes"],
                        "comments": video["comments"],
                        "shares": video["shares"]
                    }

                    await send_pretty(
                        video,
                        "🎬 <b>Новое видео опубликовано!</b>"
                    )

                else:

                    old = old_videos[video_id]

                    # ЛАЙКИ

                    if video["likes"] >= old["likes"] + 10:

                        await send_pretty(
                            video,
                            "❤️ <b>+10 лайков!</b>"
                        )

                        stats["likes"] += 10

                        old["likes"] = video["likes"]

                    # КОММЕНТЫ

                    if video["comments"] > old["comments"]:

                        await send_pretty(
                            video,
                            "💬 <b>Новый комментарий!</b>",
                            extra="""
👤 Пользователь:
someone

💬 Комментарий:
Очень круто 🔥
"""
                        )

                        stats["comments"] += 1

                        old["comments"] = video["comments"]

                    # РЕПОСТЫ

                    if video["shares"] > old["shares"]:

                        await send_pretty(
                            video,
                            "📤 <b>Кто-то поделился видео!</b>"
                        )

                        stats["shares"] += 1

                        old["shares"] = video["shares"]

            await asyncio.sleep(60)

        except Exception as e:

            print("ERROR:", e)

            await asyncio.sleep(10)

# ==================================================
# START
# ==================================================

async def on_startup(dp):

    await bot.send_message(
        chat_id=CHAT_ID,
        text="🔥 TikTok Monitor запущен!",
        reply_markup=keyboard
    )

    asyncio.create_task(
        monitor()
    )

# ==================================================
# RUN
# ==================================================

executor.start_polling(
    dp,
    skip_updates=True,
    on_startup=on_startup
)
