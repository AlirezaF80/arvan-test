import requests
from bs4 import BeautifulSoup
import hashlib
import time
import os

# --- تنظیمات ---
# آدرس سایتی که می‌خواهید چک کنید
URL_TO_MONITOR = 'https://grad.kntu.ac.ir/' 

# هر چند ثانیه یک بار سایت چک شود؟ (مثلاً 3600 برای هر ساعت)
CHECK_INTERVAL_SECONDS = 300

# اطلاعات ربات تلگرام (این‌ها را از بخش Secrets پلتفرم پارس‌پک وارد می‌کنیم)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    """یک پیام به تلگرام ارسال می‌کند."""
    if not BOT_TOKEN or not CHAT_ID:
        print("اطلاعات توکن ربات یا چت آیدی تلگرام تنظیم نشده است.")
        return
        
    api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    
    try:
        response = requests.post(api_url, data=payload)
        if response.status_code == 200:
            print("پیام با موفقیت به تلگرام ارسال شد.")
        else:
            print(f"ارسال پیام به تلگرام با خطا مواجه شد: {response.text}")
    except Exception as e:
        print(f"خطا در اتصال به API تلگرام: {e}")


def get_page_hash():
    """محتوای صفحه وب را گرفته و هش (hash) آن را برمی‌گرداند."""
    try:
        response = requests.get(URL_TO_MONITOR, timeout=15)
        response.raise_for_status() # اگر درخواست ناموفق بود، خطا ایجاد می‌کند
        
        # برای دقت بیشتر، می‌توانیم فقط بخش خاصی از سایت را هش کنیم
        # soup = BeautifulSoup(response.text, 'html.parser')
        # main_content = soup.find('main') # برای مثال تگ main
        # if main_content:
        #     return hashlib.sha256(main_content.encode('utf-8')).hexdigest()
        
        return hashlib.sha256(response.content).hexdigest()

    except requests.exceptions.RequestException as e:
        print(f"خطا در دریافت محتوای سایت: {e}")
        return None

# --- حلقه اصلی برنامه ---
if __name__ == "__main__":
    print(f"اسکریپت مانیتورینگ برای سایت {URL_TO_MONITOR} شروع به کار کرد.")
    send_telegram_message("ربات مانیتورینگ با موفقیت فعال شد.")
    
    current_hash = get_page_hash()
    if current_hash:
        print("هش اولیه سایت با موفقیت دریافت شد.")
    else:
        print("هشدار: دریافت هش اولیه ناموفق بود. برنامه بعد از وقفه زمانی دوباره تلاش خواهد کرد.")

    while True:
        # منتظر ماندن برای بازه زمانی مشخص شده
        print(f"در حال انتظار برای {CHECK_INTERVAL_SECONDS} ثانیه...")
        time.sleep(CHECK_INTERVAL_SECONDS)
        
        print("زمان بررسی مجدد فرا رسید. در حال دریافت هش جدید...")
        new_hash = get_page_hash()
        
        if new_hash and new_hash != current_hash:
            print("تغییر در سایت شناسایی شد!")
            send_telegram_message(f"توجه: سایت {URL_TO_MONITOR} آپدیت شد!")
            current_hash = new_hash # هش جدید را به عنوان هش فعلی ذخیره کن
        elif new_hash is None:
             print("هش جدید دریافت نشد. بررسی بعدی طبق زمانبندی انجام خواهد شد.")
        else:
            print("تغییری در سایت مشاهده نشد.")
