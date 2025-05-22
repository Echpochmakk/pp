import os
import requests
from telebot import types
from loguru import logger
from database import Database

db = Database()

def register_handlers(bot):
    @bot.message_handler(commands=['help'])
    def help_command(message):
        help_text = """
        Доступные команды:
        /start - Начать работу
        /help - Помощь
        /add <url> - Добавить ссылку для мониторинга
        /list - Показать все отслеживаемые ссылки
        /parse_now - Запустить проверку обновлений
        /get_last - Показать последние обновления
        """
        bot.reply_to(message, help_text)

    @bot.message_handler(commands=['add'])
    def add_link(message):
        try:
            url = message.text.split()[1]
            chat_id = message.chat.id
            
            # Save to database
            db.add_link(chat_id, url)
            
            # Send to scrapper
            scrapper_url = os.getenv('SCRAPPER_LINK_URL')
            response = requests.post(scrapper_url, json={
                'chat_id': chat_id,
                'url': url
            })
            
            if response.status_code == 200:
                bot.reply_to(message, f"Ссылка {url} добавлена для мониторинга")
            else:
                bot.reply_to(message, "Ошибка при добавлении ссылки")
                
        except IndexError:
            bot.reply_to(message, "Использование: /add <url>")
        except Exception as e:
            logger.error(f"Error in add_link: {e}")
            bot.reply_to(message, "Произошла ошибка")

    @bot.message_handler(commands=['list'])
    def list_links(message):
        try:
            chat_id = message.chat.id
            links = db.get_links(chat_id)
            
            if not links:
                bot.reply_to(message, "Нет отслеживаемых ссылок")
                return
                
            response = "Ваши ссылки:\n" + "\n".join(links)
            bot.reply_to(message, response)
            
        except Exception as e:
            logger.error(f"Error in list_links: {e}")
            bot.reply_to(message, "Произошла ошибка")

    @bot.message_handler(commands=['parse_now'])
    def parse_now(message):
        try:
            chat_id = message.chat.id
            scrapper_url = os.getenv('SCRAPPER_LINK_URL') + "/parse"
            response = requests.post(scrapper_url, json={'chat_id': chat_id})
            
            if response.status_code == 200:
                bot.reply_to(message, "Проверка обновлений запущена")
            else:
                bot.reply_to(message, "Ошибка при запуске проверки")
                
        except Exception as e:
            logger.error(f"Error in parse_now: {e}")
            bot.reply_to(message, "Произошла ошибка")

    @bot.message_handler(commands=['get_last'])
    def get_last_updates(message):
        try:
            chat_id = message.chat.id
            updates = db.get_last_updates(chat_id)
            
            if not updates:
                bot.reply_to(message, "Нет новых данных")
                return
                
            response = "Последние обновления:\n" + "\n".join(
                f"{u['url']}: {u['update']}" for u in updates
            )
            bot.reply_to(message, response)
            
        except Exception as e:
            logger.error(f"Error in get_last_updates: {e}")
            bot.reply_to(message, "Произошла ошибка")