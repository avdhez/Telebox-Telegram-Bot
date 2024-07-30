import os
import requests
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from bot.config import TELEBOX_API_TOKEN, UPLOAD_AUTH_URL, UPLOAD_FILE_URL, SHARE_FILE_URL, DOWNLOAD_FILE_URL
from bot.utils import get_file_md5

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a file to upload or a TeleBox link to download a file.')

def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document.get_file()
    file.download('temp_file')

    # Calculate MD5 of the file
    file_md5 = get_file_md5('temp_file')

    # Request upload authorization
    upload_auth_response = requests.get(UPLOAD_AUTH_URL, params={
        'fileMd5ofPre10m': file_md5,
        'fileSize': file.file_size,
        'token': TELEBOX_API_TOKEN
    })
    upload_auth_data = upload_auth_response.json()

    if upload_auth_data['status'] == 1:
        sign_url = upload_auth_data['data']['signUrl']

        # Upload the file
        with open('temp_file', 'rb') as f:
            upload_response = requests.put(sign_url, data=f)

        if upload_response.status_code == 200:
            # Create file item in TeleBox
            upload_file_response = requests.get(UPLOAD_FILE_URL, params={
                'fileMd5ofPre10m': file_md5,
                'fileSize': file.file_size,
                'pid': 0,
                'diyName': update.message.document.file_name,
                'token': TELEBOX_API_TOKEN
            })
            upload_file_data = upload_file_response.json()

            if upload_file_data['status'] == 1:
                file_id = upload_file_data['data']['itemId']
                share_response = requests.get(SHARE_FILE_URL, params={
                    'itemIds': file_id,
                    'expire_enum': 4,  # Permanent
                    'token': TELEBOX_API_TOKEN
                })
                share_data = share_response.json()
                share_token = share_data['data']['shareToken']
                update.message.reply_text(f'File uploaded successfully. Share link: https://www.linkbox.to/{share_token}')
            else:
                update.message.reply_text('Failed to create file item in TeleBox.')
        else:
            update.message.reply_text('Failed to upload the file.')
    else:
        update.message.reply_text('Failed to get upload authorization.')

    os.remove('temp_file')

def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if 'linkbox.to' in text:
        # Extract file ID from the link
        file_id = text.split('/')[-1]
        
        # Search for the file in TeleBox
        search_response = requests.get(DOWNLOAD_FILE_URL, params={
            'name': file_id,
            'pid': 0,
            'token': TELEBOX_API_TOKEN,
            'pageNo': 1,
            'pageSize': 1
        })
        search_data = search_response.json()

        if search_data['status'] == 1 and search_data['data']['list']:
            file_info = search_data['data']['list'][0]
            file_url = file_info['cover']  # Example of file URL, adjust based on your needs
            update.message.reply_text(f'File URL: {file_url}')
        else:
            update.message.reply_text('File not found in TeleBox.')
    else:
        update.message.reply_text('Please send a valid TeleBox link.')