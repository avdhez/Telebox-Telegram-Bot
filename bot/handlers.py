# handlers.py

import os
import requests
from telegram import Update
from telegram.ext import CallbackContext
from .config import TELEBOX_API_TOKEN, SEARCH_FILE_URL, DOWNLOAD_FILE_URL
from .utils import update_progress_message

def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    if 'linkbox.to' in text:
        # Extract file ID from the link
        file_id = text.split('/')[-1]
        
        # Fetch file details from TeleBox
        search_response = requests.get(SEARCH_FILE_URL, params={
            'name': file_id,
            'pid': 0,
            'token': TELEBOX_API_TOKEN,
            'pageNo': 1,
            'pageSize': 1
        })
        search_data = search_response.json()

        if search_data['status'] == 1 and search_data['data']['list']:
            file_info = search_data['data']['list'][0]
            file_url = file_info['cover']  # Adjust this based on actual file URL field

            # Send progress update message
            progress_message = update.message.reply_text("Downloading file...")

            # Download the file with progress bar
            response = requests.get(file_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open('downloaded_file', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    update_progress_message(context.bot, chat_id, progress_message.message_id, downloaded_size, total_size)

            # Send the downloaded file
            context.bot.send_document(chat_id=chat_id, document=open('downloaded_file', 'rb'))

            # Cleanup
            os.remove('downloaded_file')
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress_message.message_id,
                text='File downloaded successfully.'
            )
        else:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='File not found in TeleBox.'
            )
    else:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Please send a valid TeleBox link.'
        )