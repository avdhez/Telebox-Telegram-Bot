# utils.py

from telegram import Bot

def update_progress_message(bot: Bot, chat_id: int, message_id: int, downloaded: int, total: int) -> None:
    progress = int((downloaded / total) * 100)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Download progress: {progress}%"
    )