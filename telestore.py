import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging

# Replace with your actual tokens and IDs
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
STORAGE_CHANNEL_ID = -1001234567890 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

def start(update, context):
    update.message.reply_text("Send me a file to store, or send a previously generated file link to retrieve it.")

def handle_file(update, context):
    try:
        file = update.message.document.get_file()
        file_name = file.file_name
        file.download(f'downloads/{file_name}')  

        result = context.bot.send_document(
            chat_id=STORAGE_CHANNEL_ID,
            document=open(f'downloads/{file_name}', 'rb')
        )

        message_link = result.message_link
        update.message.reply_text(f"Your file has been stored. Access it here: {message_link}")

        os.remove(f'downloads/{file_name}')  # Clean up downloaded file

    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

def handle_link(update, context):
    try:
        file_id = extract_file_id_from_link(update.message.text) 
        file = context.bot.get_file(file_id)
        file.download('temp_download.file')
        context.bot.send_document(update.chat_id, open('temp_download.file', 'rb'))
        os.remove('temp_download.file')

    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

def extract_file_id_from_link(link):
    # Implement your logic to extract the file ID from the Telegram message link
    # Example using regular expressions if the link format is consistent:
    import re
    match = re.search(r'https://t.me/c/\d+/(?P<file_id>\d+)', link)
    if match:
        return match.group('file_id')
    else:
        raise ValueError("Invalid file link format")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(MessageHandler(Filters.text, handle_link)) 

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
