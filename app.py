import requests
from bs4 import BeautifulSoup
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# --- تنظیمات اصلی ---
# آدرس سایتی که می‌خواهید چک کنید
URL_TO_CHECK = 'https://grad.kntu.ac.ir' 
# نام فایلی برای ذخیره آخرین وضعیت سایت
HASH_FILE = 'last_hash.txt'

# --- تنظیمات ایمیل (این مقادیر از Environment Variables خوانده می‌شوند) ---
SMTP_SERVER = os.environ.get('SMTP_SERVER') # مثلا: 'smtp.gmail.com'
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # پسورد ایمیل یا App Password
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

def send_notification_email(subject, body):
    """تابعی برای ارسال ایمیل نوتیفیکیشن"""
    if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("خطا: متغیرهای محیطی برای ارسال ایمیل به درستی تنظیم نشده‌اند.")
        return

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

        print("در حال اتصال به سرور SMTP...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # فعال‌سازی امنیت
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("لاگین موفقیت‌آمیز بود.")
        
        server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        print(f"ایمیل با موفقیت به {RECIPIENT_EMAIL} ارسال شد.")
        server.quit()
    except Exception as e:
        print(f"خطا در ارسال ایمیل: {e}")

def get_page_hash():
    """محتوای سایت را گرفته و یک هش از آن برمی‌گرداند"""
    try:
        response = requests.get(URL_TO_CHECK, timeout=15)
        response.raise_for_status()
        # برای دقت بیشتر، می‌توانید فقط بخش خاصی از صفحه را هش کنید
        # soup = BeautifulSoup(response.text, 'html.parser')
        # content = soup.find('main').encode('utf-8')
        return hashlib.sha256(response.content).hexdigest()
    except requests.RequestException as e:
        print(f"خطا در دریافت محتوای سایت: {e}")
        return None

def main():
    print("شروع بررسی سایت...")
    
    # خواندن هش قبلی از فایل
    try:
        with open(HASH_FILE, 'r') as f:
            last_hash = f.read().strip()
    except FileNotFoundError:
        last_hash = None
        print("فایل هش پیدا نشد، برای اولین بار اجرا می‌شود.")

    new_hash = get_page_hash()

    if new_hash and new_hash != last_hash:
        print(f"تغییر شناسایی شد! هش جدید: {new_hash}")
        # ارسال ایمیل
        subject = f"تغییر در سایت {URL_TO_CHECK}"
        body = f"سایت مورد نظر شما آپدیت شده است.\n\nآدرس سایت: {URL_TO_CHECK}"
        send_notification_email(subject, body)
        
        # ذخیره هش جدید در فایل
        with open(HASH_FILE, 'w') as f:
            f.write(new_hash)
            
    elif not new_hash:
        print("هش جدید دریافت نشد. بررسی ناموفق بود.")
    else:
        print("هیچ تغییری یافت نشد.")

if __name__ == "__main__":
    main()
