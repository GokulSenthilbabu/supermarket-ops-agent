import os
import json
import asyncio

from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Bot

from app.agent import run_agent

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def process_message(chat_id, text):
    response = run_agent(
        text,
        user_id=str(chat_id)
    )

    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=chat_id,
        text=response
    )

    await bot.shutdown()


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            update = json.loads(body)

            message = update.get("message")

            if message:
                text = message.get("text")

                if text:
                    chat_id = message["chat"]["id"]

                    asyncio.run(
                        process_message(chat_id, text)
                    )

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as exc:
            print(f"Webhook error: {exc}")

            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Supermarket Ops Agent is running")