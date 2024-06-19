import logging
import os
import requests
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your Telegram bot token and group chat ID from .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check if Instagram account exists and its privacy status
def check_instagram_account(username):
    # Placeholder function
    # You need to implement this function to check the Instagram account status
    # For now, let's assume it always returns 'public'
    return 'public'

# Function to retrieve user data from the group chat
async def get_user_data(context, chat_id):
    messages = await context.bot.get_chat_history(GROUP_CHAT_ID, limit=100)
    for message in messages:
        if str(chat_id) in message.text:
            return message.text
    return None

# Function to update user data in the group chat
async def update_user_data(context, chat_id, update_count, downloaded_photos):
    messages = await context.bot.get_chat_history(GROUP_CHAT_ID, limit=100)
    for message in messages:
        if str(chat_id) in message.text:
            await context.bot.edit_message_text(
                chat_id=GROUP_CHAT_ID,
                message_id=message.message_id,
                text=f"ChatID: {chat_id}, Update: {update_count}, Downloaded Photos: {downloaded_photos}"
            )
            return
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"ChatID: {chat_id}, Update: {update_count}, Downloaded Photos: {downloaded_photos}"
    )

# Command handler for /start
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    user_data = await get_user_data(context, chat_id)

    if user_data is None:
        user_update = 0
        downloaded_photo = 0
        await update_user_data(context, chat_id, user_update, downloaded_photo)
    else:
        user_info = user_data.split(', ')
        user_update = int(user_info[1].split(': ')[1])
        downloaded_photo = int(user_info[2].split(': ')[1])

    context.user_data['update'] = user_update
    context.user_data['downloaded_photo'] = downloaded_photo

    await update.message.reply_text('Enter Instagram username:')

# Message handler to process Instagram username input
async def process_username(update: Update, context: CallbackContext) -> None:
    username = update.message.text.strip()

    # Check Instagram account details
    account_status = check_instagram_account(username)

    if account_status == 'not_found':
        await update.message.reply_text('Username not available.')
    elif account_status == 'private':
        await update.message.reply_text('Downloading data of Private account is not available freely. '
                                        'Buy premium membership to download data of Private Account.')
    elif account_status == 'public':
        context.user_data['username'] = username
        await update.message.reply_text('Account is public. How many photos do you want to download?',
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
async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_option = int(query.data)
    chat_id = query.message.chat_id

    user_data = await get_user_data(context, chat_id)
    user_info = user_data.split(', ')
    user_update = int(user_info[1].split(': ')[1])
    downloaded_photo = int(user_info[2].split(': ')[1])

    if downloaded_photo + selected_option > 50:
        await query.answer()
        await query.message.reply_text('Limit exhausted. Please buy premium to download more.')
    else:
        await download_photos(query, context, chat_id, context.user_data['username'], selected_option)
        new_total = downloaded_photo + selected_option
        new_update = user_update + 1

        await update_user_data(context, chat_id, new_update, new_total)

# Function to download photos and send to the user
async def download_photos(query, context, chat_id, username, num_photos):
    # Placeholder function
    # You need to implement this function to download photos from Instagram
    photo_urls = []  # Replace with actual logic to get photo URLs from Instagram

    # Example placeholder URLs (replace these with actual URLs from Instagram)
    for i in range(num_photos):
        photo_urls.append(f'https://example.com/photo_{i}.jpg')

    for photo_url in photo_urls:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_url)

    await query.answer()
    await query.message.reply_text(f'Downloaded {num_photos} photos.')

# Initialize Flask app
app = Flask(__name__)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

def main():
    # Set up application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_username))
    application.add_handler(CallbackQueryHandler(button_click))

    # Start webhook
    application.run_webhook(listen='0.0.0.0',
                            port=8443,
                            url_path=TELEGRAM_BOT_TOKEN,
                            webhook_url=f'https://insta-upload-downloader.onrender.com/{TELEGRAM_BOT_TOKEN}')

if __name__ == '__main__':
    main()
