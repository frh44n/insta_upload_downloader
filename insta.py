import logging
import sqlite3
import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your Telegram bot token from .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLite database
conn = sqlite3.connect('user_data.db', check_same_thread=False)
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY, username TEXT, total_photos_downloaded INTEGER)''')
conn.commit()

# Function to check if Instagram account exists and its privacy status
def check_instagram_account(username):
    # Placeholder function
    # You need to implement this function to check the Instagram account status
    # For now, let's assume it always returns 'public'
    return 'public'

# Command handler for /start
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.user_data['username'] = None
    context.user_data['total_photos_downloaded'] = 0

    update.message.reply_text('Enter Instagram username:')

# Message handler to process Instagram username input
def process_username(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    username = update.message.text.strip()

    # Check Instagram account details
    account_status = check_instagram_account(username)

    if account_status == 'not_found':
        update.message.reply_text('Username not available.')
    elif account_status == 'private':
        update.message.reply_text('Downloading data of Private account is not available freely. '
                                  'Buy premium membership to download data of Private Account.')
    elif account_status == 'public':
        context.user_data['username'] = username
        update.message.reply_text('Account is public. How many photos do you want to download?',
                                  reply_markup=create_inline_keyboard())

# Function to create inline keyboard with download options
def create_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("10 images", callback_data='10')],
        [InlineKeyboardButton("20 images", callback_data='20')],
        [InlineKeyboardButton("30 images", callback_data='30')],
        [InlineKeyboardButton("40 images", callback_data='40')],
        [InlineKeyboardButton("50 images", callback_data='50')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Callback query handler for inline keyboard selection
def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_option = int(query.data)

    chat_id = query.message.chat_id
    username = context.user_data['username']
    total_photos_downloaded = context.user_data['total_photos_downloaded']

    if total_photos_downloaded >= 50:
        query.answer()
        query.message.reply_text('Limit exhausted. Please buy premium to download more.')
    else:
        download_photos(chat_id, username, selected_option)
        context.user_data['total_photos_downloaded'] += selected_option

# Function to download photos
def download_photos(chat_id, username, num_photos):
    # Placeholder function
    # You need to implement this function to download photos from Instagram
    pass

# Initialize Flask app
app = Flask(__name__)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

def main():
    # Set up webhook
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_username))
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    # Start webhook
    updater.start_webhook(listen='0.0.0.0',
                          port=8443,
                          url_path=TELEGRAM_BOT_TOKEN)
    updater.bot.set_webhook(f'https://your_domain.com/{TELEGRAM_BOT_TOKEN}')

    # Run Flask app
    app.run(port=8443)

if __name__ == '__main__':
    main()
