import asyncio
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

# ======================================================
# ДАННЫЕ
# ======================================================

TELEGRAM_BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"

CHAT_ID = "5296078628"

TIKTOK_USERNAME = "stxz.ed1ts"

CLIENT_KEY = "aws9c59qtbjw446y"
CLIENT_SECRET = "rriXqmqBtgQUkDcD3uzuuBEUikxxa0NT"

# ======================================================
# BOT
# ======================================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# ======================================================
# КНОПКИ
# ======================================================

keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

keyboard.add(
    KeyboardButton("📊 Статистика")
)

keyboard.add(
    KeyboardButton("🔥 Проверить")
)

keyboard.add(
    KeyboardButton("👁 Теневой бан")
)

# ======================================================
# ПАМЯТЬ
# ======================================================

old_videos = {}

hour_stats = {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "followers": 0
}

# ======================================================
# ЭМОДЗИ
# ======================================================

LIKE = "❤️"
COMMENT = "💬"
VIDEO = "🎬"
SHARE = "📤"
FOLLOW = "👥"
FIRE = "🔥"

# ======================================================
# ПОЛУЧЕНИЕ ВИДЕО
# ======================================================

def get_videos():

    # ТЕСТОВЫЕ ДАННЫЕ
    # МОЖНО ПОТОМ ПОДКЛЮЧИТЬ API

    likes = random.randint(100, 300)
    comments = random.randint(1, 50)
    shares = random.randint(1, 20)

    fake_data = [
        {
            "id": "1",

            "title": "TikTok Video",

            "likes": likes,

            "comments": comments,

            "shares": shares,

            "url": f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/1"
        }
    ]

    return fake_data

# ======================================================
# КРАСИВОЕ СООБЩЕНИЕ
# ======================================================

async def send_pretty_message(
    video,
    event_type,
    extra_text=""
):

    text = f"""
🔥 <b>TikTok Monitor</b>

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

# ======================================================
# ТЕНЕВОЙ БАН
# ======================================================

def check_shadow_ban(video):

    estimated_views = video["likes"] * 10

    if estimated_views < 150:

        return True

    return False

# ======================================================
# КНОПКА СТАТИСТИКА
# ======================================================

@dp.message_handler(
    lambda message: message.text == "📊 Статистика"
)
async def stats_handler(message: types.Message):

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

    await message.answer(
        text,
        parse_mode="HTML"
    )

# ======================================================
# КНОПКА ПРОВЕРКА
# ======================================================

@dp.message_handler(
    lambda message: message.text == "🔥 Проверить"
)
async def check_handler(message: types.Message):

    videos = get_videos()

    for video in videos:

        await send_pretty_message(
            video,
            "🔥 Ручная проверка"
        )

# ======================================================
# ТЕНЕВОЙ БАН
# ======================================================

@dp.message_handler(
    lambda message: message.text == "👁 Теневой бан"
)
async def shadow_handler(message: types.Message):

    videos = get_videos()

    result = "✅ Теневого бана нет"

    for video in videos:

        if check_shadow_ban(video):

            result = """
⚠️ Возможен теневой бан

Причины:
• Малый охват
• Видео плохо залетает
• Низкие просмотры
"""

    await message.answer(result)

# ======================================================
# START
# ======================================================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    text = f"""
🔥 <b>TikTok Monitor запущен!</b>

👤 Аккаунт:
@{TIKTOK_USERNAME}

✅ Бот работает
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ======================================================
# МОНИТОРИНГ
# ======================================================

async def monitor():

    global old_videos

    while True:

        try:

            videos = get_videos()

            for video in videos:

                video_id = video["id"]

                # ======================================
                # НОВОЕ ВИДЕО
                # ======================================

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

                    # ======================================
                    # ЛАЙКИ
                    # ======================================

                    if video["likes"] >= old["likes"] + 10:

                        await send_pretty_message(
                            video,
                            "❤️ <b>+10 лайков!</b>"
                        )

                        hour_stats["likes"] += 10

                        old["likes"] = video["likes"]

                    # ======================================
                    # КОММЕНТЫ
                    # ======================================

                    if video["comments"] > old["comments"]:

                        await send_pretty_message(
                            video,
                            "💬 <b>Новый комментарий!</b>",
                            extra_text="""
👤 Пользователь:
someone

💬 Комментарий:
Очень круто 🔥
"""
                        )

                        hour_stats["comments"] += 1

                        old["comments"] = video["comments"]

                    # ======================================
                    # РЕПОСТЫ
                    # ======================================

                    if video["shares"] > old["shares"]:

                        await send_pretty_message(
                            video,
                            "📤 <b>Кто-то поделился видео!</b>"
                        )

                        hour_stats["shares"] += 1

                        old["shares"] = video["shares"]

            await asyncio.sleep(60)

        except Exception as e:

            print("ERROR:", e)

            await asyncio.sleep(10)

# ======================================================
# STARTUP
# ======================================================

async def on_startup(_):

    print("BOT STARTED")

    await bot.send_message(
        CHAT_ID,
        "🔥 TikTok Monitor успешно запущен!"
    )

    asyncio.create_task(
        monitor()
    )

# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )
