import os
import re
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.agent import run_agent, reset_chat

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Welcome to Supermarket Ops Agent!\n\n"
        "I can manage inventory, billing, Khata and analytics.\n\n"
        "Try:\n"
        "• Search Maggi\n"
        "• Show today's sales\n"
        "• Create weekly sales report"
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    reset_chat(user_id)

    await update.message.reply_text(
        "🔄 New chat started.\n"
        "Your saved preferences are still remembered."
    )


def find_artifacts(response: str):
    """Find generated PDF/PPTX paths mentioned by the agent."""

    artifacts = []

    paths = re.findall(
        r'([A-Za-z]:[\\/][^\n\r]+?\.(?:pdf|pptx))',
        response,
        re.IGNORECASE,
    )

    for path in paths:
        path = path.strip().strip('"').strip("'")

        if Path(path).exists():
            artifacts.append(path)

    return artifacts


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = str(update.effective_user.id)
    message = update.message.text

    await update.message.chat.send_action("typing")

    response = run_agent(
        message,
        user_id=user_id
    )

    artifacts = find_artifacts(response)

    # Remove local Windows path from the message sent to Telegram
    clean_response = re.sub(
        r'\s*[A-Za-z]:[\\/][^\n\r]+?\.(?:pdf|pptx)',
        '',
        response,
        flags=re.IGNORECASE,
    ).strip()

    if clean_response:
        await update.message.reply_text(clean_response)

    for artifact in artifacts:
        suffix = Path(artifact).suffix.lower()

        try:
            if suffix == ".pdf":
                with open(artifact, "rb") as file:
                    await update.message.reply_document(
                        document=file,
                        caption="📄 Invoice PDF"
                    )

            elif suffix == ".pptx":
                with open(artifact, "rb") as file:
                    await update.message.reply_document(
                        document=file,
                        caption="📊 Weekly Sales Analysis"
                    )

        except Exception as exc:
            await update.message.reply_text(
                f"Could not send the generated file: {exc}"
            )


def main():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing from .env"
        )

    application = Application.builder().token(TOKEN).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("new", new_chat)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Telegram bot started...")

    application.run_polling()


if __name__ == "__main__":
    main()