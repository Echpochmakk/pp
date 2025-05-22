import os
import telebot
from dotenv import load_dotenv
from loguru import logger
from handler import register_handlers

# Load environment variables
load_dotenv()

# Initialize bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Configure logger
logger.add("bot.log", rotation="10 MB", format="{time} {level} {message}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для мониторинга ресурсов. Используй /help для списка команд.")

# Register all handlers
register_handlers(bot)

# Start HTTP server for notifications
if __name__ == '__main__':
    from flask import Flask, request
    app = Flask(__name__)
    
    @app.route('/bot/notify', methods=['POST'])
    def handle_notification():
        data = request.json
        chat_id = data['chat_id']
        message = data['message']
        bot.send_message(chat_id, message)
        return {'status': 'ok'}
    
    # Start bot polling and Flask server
    import threading
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': os.getenv('BOT_SERVER_PORT')}).start()
    bot.polling()