import os
import django
import telebot


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()


from inventory.models import Stock, Product
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

def send_deficit_notification(product_name, current_qty, min_qty):
    message = (
        f"⚠️ **ДЕФИЦИТ ТОВАРА!**\n\n"
        f"📦 Товар: {product_name}\n"
        f"📉 Остаток: {current_qty} шт.\n"
        f"🛑 Минимум: {min_qty} шт.\n\n"
        f"Пора оформить закупку!"
    )
    try:
        bot.send_message(CHAT_ID, message, parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling()