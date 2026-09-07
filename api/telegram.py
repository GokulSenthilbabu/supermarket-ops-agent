import os

from dotenv import load_dotenv
from telegram import Bot
from app.agent import run_agent

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    try:
        update = await request.json()

        message = update.get("message")

        if not message:
            return {
                "statusCode": 200,
                "body": "OK"
            }

        text = message.get("text")

        if not text:
            return {
                "statusCode": 200,
                "body": "OK"
            }

        chat_id = str(message["chat"]["id"])

        response = run_agent(
            text,
            user_id=chat_id
        )

        bot = Bot(token=TOKEN)

        await bot.send_message(
            chat_id=chat_id,
            text=response
        )

        return {
            "statusCode": 200,
            "body": "OK"
        }

    except Exception as exc:
        print(f"Webhook error: {exc}")

        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }