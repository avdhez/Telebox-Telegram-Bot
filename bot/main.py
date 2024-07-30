# main.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot.handlers import handle_text

def main():
    # Replace 'YOUR_BOT_API_TOKEN' with your actual bot API token
    updater = Updater("YOUR_BOT_API_TOKEN")
    dispatcher = updater.dispatcher

    # Add handlers for text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # Start polling for updates
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()