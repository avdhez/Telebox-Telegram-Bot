import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEBOX_API_KEY = 'YOUR_TELEBOX_API_KEY'

def download_file(update, context):
    file_id = update.message.document.file_id
    file_info = context.bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'

    # Download file to OS
    response = requests.get(file_url, stream=True)
    file_path = f'/app/{file_info.file_name}'
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    # Upload file to Telebox
    upload_url = f'https://api.telebox.online/get_upload_url'
    response = requests.post(upload_url, headers={'Authorization': f'Bearer {TELEBOX_API_KEY}'})
    upload_url = response.json()['upload_url']

    files = {'file': open(file_path, 'rb')}
    response = requests.put(upload_url, files=files)
    file_id = response.json()['file_id']

    # Share file on Telebox
    share_url = f'https://api.telebox.online/files/{file_id}/share'
    response = requests.post(share_url, headers={'Authorization': f'Bearer {TELEBOX_API_KEY}'})
    share_url = response.json()['share_url']

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'File uploaded to Telebox! Here is the link: {share_url}')

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.document, download_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()