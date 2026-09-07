import os
import json
import asyncio
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler

from dotenv import load_dotenv
from telegram import Bot

from app.agent import run_agent

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def find_files(response):
    files = []

    patterns = [
        r'[A-Za-z]:[\\/][^\n\r"]+\.(pdf|pptx)',
        r'(?:generated_invoices|generated_reports)[\\/][^\n\r"]+\.(pdf|pptx)',
        r'/tmp/[^\n\r"]+\.(pdf|pptx)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)

        for match in matches:
            if isinstance(match, tuple):
                continue

            path = Path(match)

            if path.exists() and path.is_file():
                files.append(path)

    return list(dict.fromkeys(files))


async def process_message(chat_id, text):
    bot = Bot(token=TOKEN)

    try:
        response = run_agent(
            text,
            user_id=str(chat_id)
        )

        if not response:
            response = "I couldn't process that request."

        await bot.send_message(
            chat_id=chat_id,
            text=str(response)
        )

        files = find_files(str(response))

        for file_path in files:
            try:
                with open(file_path, "rb") as file:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=file,
                        caption=file_path.name
                    )
            except Exception as file_error:
                print(
                    f"File send error: {file_error}"
                )

    except Exception as exc:
        print(
            f"Agent error: {exc}"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=f"Agent error: {exc}"
        )

    finally:
        await bot.shutdown()


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(length)

            update = json.loads(body)

            message = update.get("message")

            if message:
                text = message.get("text")

                if text:
                    chat_id = message["chat"]["id"]

                    asyncio.run(
                        process_message(
                            chat_id,
                            text
                        )
                    )

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain"
            )

            self.end_headers()

            self.wfile.write(b"OK")

        except Exception as exc:
            print(
                f"Webhook error: {exc}"
            )

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "text/plain"
            )

            self.end_headers()

            self.wfile.write(
                b"Internal Server Error"
            )

    def do_GET(self):
        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()

        self.wfile.write(
            b"Supermarket Ops Agent is running"
        )