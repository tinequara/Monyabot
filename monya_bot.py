import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram import Router
import json
from datetime import datetime, timezone
from aiogram.exceptions import TelegramBadRequest
import time

TELEGRAM_TOKEN = "test" # bez podruzki v .env
NEUROAPI_KEY = "test"
router = Router()

AUTHORIZED_USER_ID = 372971692
NICKS = ["моня", "монь"]
is_active = True
def ask_neuroapi(user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {NEUROAPI_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Ты Моня, владелец чери арризо 8 и участник чата. У всех такая же машина как и у тебя"
        "Веди себя как реальный человек. Отвечай логично, коротко и иногда с матом."
        "На вопросы отвечай, используя интернет.Иногда пропускай знаки препинания и допускай ошибки."
    )

    data = {
        "model": "gemini-2.0-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    }

    url = "https://neuroapi.host/v1/chat/completions"

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        logging.error(f"NeuroAPI error {response.status_code}: {response.text}")
        return ""

    resp_json = response.json()
    return resp_json["choices"][0]["message"]["content"]

async def is_chat_open(bot: Bot, chat_id: int) -> bool:
    try:
        chat = await bot.get_chat(chat_id)
        if chat.type in ["group", "supergroup", "channel"]:
            return True
        return False
    except TelegramBadRequest as e:
        logging.error(f"Ошибка при получении чата {chat_id}: {e}")
        return False

def chunk_text(text: str, max_length=4000) -> list[str]:
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@router.message(lambda m: m.text and m.text.lower() in ["/start", "/stop"])
async def command_handler(message: types.Message, bot: Bot):
    global is_active

    if message.from_user.id != AUTHORIZED_USER_ID:
        await message.reply("⚠ У тебя нет доступа к команде. По всем вопросам: @beszpredel")
        return

    if message.text.lower() == "/stop":
        is_active = False
        await message.reply("💤 Моня ушел отдыхать")
        logging.info(f"Бот остановлен пользователем {message.from_user.id}")
    elif message.text.lower() == "/start":
        is_active = True
        await message.reply("💬 Моня снова тут и готов помогать")
        logging.info(f"Бот запущен пользователем {message.from_user.id}")

@router.message(lambda m: m.text and m.text.lower() == "/info")
async def info_handler(message: types.Message, bot: Bot):
    if message.from_user.id != AUTHORIZED_USER_ID:
        await message.reply("⚠ У тебя нет доступа к команде. По всем вопросам: @beszpredel")
        return
    info_text = (
        "🤖 Меня зовут Моня Ким, саркастичный и глуповатый ИИ: \n"
        "- русскоязычный китаец, который собирал твою арризу;\n"
        "- отвечаю в чате на упоминание Моня, или если ответить на сообщение;\n"
        "- являюсь участником чата и помощником.\n"
    )
    await message.reply(info_text, parse_mode="Markdown")
    logging.info(f"Пользователь {message.from_user.id} отправил информацию о боте в чат.")

@router.message()
async def group_handler(message: types.Message, bot: Bot):
    global is_active
    if not is_active:
        return

    if message.chat.type == "private":
        return

    me = await bot.get_me()

    if message.from_user and message.from_user.id == me.id:
        return

    if not message.text:
        return

    message_time = message.date.replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)

    if (current_time - message_time).total_seconds() > 30:
        return

    text_lower = message.text.lower()
    mentioned_by_nick = any(nick in text_lower for nick in NICKS)

    is_reply_to_bot = (
        message.reply_to_message is not None and
        message.reply_to_message.from_user is not None and
        message.reply_to_message.from_user.id == me.id
    )

    if not mentioned_by_nick and not is_reply_to_bot:
        return

    user_text = message.text.strip()

    if not user_text and is_reply_to_bot and message.reply_to_message.text:
        user_text = message.reply_to_message.text.strip()

    if not user_text:
        return

    start_time = time.monotonic()
    reply = ask_neuroapi(user_text)
    end_time = time.monotonic()

    if not reply or len(reply.strip()) == 0:
        return

    chunks = chunk_text(reply)
    for chunk in chunks:
        try:
            chat_id = message.chat.id
            if await is_chat_open(bot, chat_id):
                await message.reply(chunk)
            else:
                logging.error(f"Чат {chat_id} закрыт, не могу отправить сообщение.")
        except TelegramBadRequest as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
        except Exception as e:
            logging.error(f"Необработанная ошибка: {e}")

    delay = end_time - start_time
    logging.info(
        f"Бот ответил с задержкой {delay:.2f} секунд"
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
