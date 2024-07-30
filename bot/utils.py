import hashlib
import os
import requests
from telegram import Bot

def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def update_progress_message(bot: Bot, chat_id: int, message_id: int, progress: int, total: int) -> None:
    progress_percentage = int((progress / total) * 100)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Progress: {progress_percentage}%"
    )