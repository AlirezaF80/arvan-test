import requests
from bs4 import BeautifulSoup
import hashlib
import time
import os
import sys

# آدرس سایت مورد نظر برای مانیتورینگ
URL = 'https://grad.kntu.ac.ir/' 

# نام فایلی برای ذخیره هش قبلی
HASH_FILE = 'last_hash.txt'

def get_page_hash():
    """محتوای صفحه را گرفته و هش آن را برمی‌گرداند"""
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
        # می‌توانید فقط بخش خاصی از صفحه را برای دقت بیشتر انتخاب کنید
        # soup = BeautifulSoup(response.text, 'html.parser')
        # main_content = soup.find('main')
        # if main_content:
        #     return hashlib.sha256(main_content.encode()).hexdigest()
        return hashlib.sha256(response.content).hexdigest()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def read_last_hash():
    """هش قبلی را از فایل می‌خواند"""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return f.read().strip()
    return None

def write_new_hash(new_hash):
    """هش جدید را در فایل می‌نویسد"""
    with open(HASH_FILE, 'w') as f:
        f.write(new_hash)

def send_telegram_message(message):
    """ارسال پیام به تلگرام با استفاده از متغیرهای محیطی"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set.")
        sys.exit(1) # از برنامه خارج شو تا متوجه خطا بشوی
        
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=payload, timeout=10)
        print("Notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

# --- منطق اصلی اسکریپت ---
def main():
    print("Starting check...")
    last_hash = read_last_hash()
    new_hash = get_page_hash()
    
    if new_hash and new_hash != last_hash:
        print(f"Change detected! New hash: {new_hash}")
        send_telegram_message(f"سایت {URL} به‌روزرسانی شد!")
        write_new_hash(new_hash)
    elif not new_hash:
        print("Could not fetch new hash. Skipping.")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
