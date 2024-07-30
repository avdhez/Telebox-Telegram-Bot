import os
import requests
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

from .telebox import Telebox
from .config import Config

# Initialize Telebox client
telebox = Telebox(Config.TELEBOX_API, Config.TELEBOX_BASEFOLDER)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! Send me a file to upload to Telebox or a Telebox link to download.')

async def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document or update.message.video or update.message.photo[-1]

    # Download the file
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)
    file_path = new_file.download()

    # Upload to Telebox
    folder_id = Config.TELEBOX_BASEFOLDER
    telebox.upload.upload_file(file_path, folder_id)

    # Notify user
    await update.message.reply_text('File uploaded to Telebox successfully!')

    # Clean up local file
    os.remove(file_path)

async def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if 'linkbox.to' in text:  # Check if the message contains a Telebox link
        try:
            await download_and_send_telebox_file(update, context, text)
        except Exception as e:
            await update.message.reply_text(f"Failed to download file: {str(e)}")
    else:
        await update.message.reply_text('Please send a file or a valid Telebox link.')

async def download_and_send_telebox_file(update: Update, context: CallbackContext, link: str) -> None:
    # Extract the file ID from the Telebox link
    file_id = extract_file_id_from_link(link)

    # Get file details from Telebox
    file_details = telebox.folder.get_details(file_id)

    if file_details['status'] != 1:
        await update.message.reply_text('Could not find the file on Telebox.')
        return

    file_url = file_details['data']['fileUrl']
    file_name = file_details['data']['name']

    # Download the file
    response = requests.get(file_url, stream=True)
    file_path = os.path.join('/tmp', file_name)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Send the file to the user
    with open(file_path, 'rb') as f:
        await update.message.reply_document(document=InputFile(f, filename=file_name))

    # Clean up local file
    os.remove(file_path)

def extract_file_id_from_link(link: str) -> str:
    # Implement logic to extract file ID from the Telebox link
    # Assuming the link format is something like: https://www.linkbox.to/file/{file_id}
    return link.split('/')[-1]

def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(Config.TELEGRAM_API_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.PHOTO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()