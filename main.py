import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tqdm import tqdm

TOKEN = '7086505429:AAEXdqa_LA2shyxeW1jd6WKlJwMcJ-W6T6E'
TELEBOX_API_KEY = '24lAbSDb9KbMTz8K'

def download_file(update, context):
    file_id = update.message.document.file_id
    file_info = context.bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'

    # Download file to OS
    response = requests.get(file_url, stream=True)
    file_path = f'/app/{file_info.file_name}'
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True)
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(block_size):
            f.write(chunk)
            t.update(len(chunk))
    t.close()

    # Upload file to Telebox
    upload_url = f'https://api.telebox.online/get_upload_url'
    response = requests.post(upload_url, headers={'Authorization': f'Bearer {TELEBOX_API_KEY}'})
    upload_url = response.json()['upload_url']

    files = {'file': open(file_path, 'rb')}
    total_size = os.path.getsize(file_path)
    block_size = 1024
    t = tqdm(total=total_size, unit='B', unit_scale=True)
    response = requests.put(upload_url, files=files, stream=True)
    for chunk in response.iter_content(block_size):
        t.update(len(chunk))
    t.close()

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