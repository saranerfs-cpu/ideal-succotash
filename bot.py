import asyncio
import requests
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ============================================
# ДАННЫЕ
# ============================================

TELEGRAM_BOT_TOKEN = "8976617638:AAEuq3jTKCr9vL61wuCFhOIGBq8d0hheAIA"
CHAT_ID = "5296078628"

TIKTOK_USERNAME = "stxz.ed1ts"

CLIENT_KEY = "aws9c59qtbjw446y"
CLIENT_SECRET = "rriXqmqBtgQUkDcD3uzuuBEUikxxa0NT"

# ============================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

last_followers = 0


async def check_followers():
    global last_followers

    while True:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"

            response = requests.get(url, headers=headers)

            match = re.search(r'"followerCount":(\d+)', response.text)

            if match:
                followers = int(match.group(1))

                if last_followers == 0:
                    last_followers = followers

                if followers > last_followers:
                    diff = followers - last_followers

                    await bot.send_message(
                        CHAT_ID,
                        f"🔥 Новый подписчик!\n\nВсего: {followers}\n+{diff}"
                    )

                    last_followers = followers

                print("Подписчики:", followers)

            else:
                print("Не удалось получить данные")

        except Exception as e:
            print("Ошибка:", e)

        await asyncio.sleep(60)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот работает")


async def main():
    asyncio.create_task(check_followers())
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
