import os
import traceback
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Monky Bot is active and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # 1. تشغيل سيرفر الويب أولاً ليبقى رندر سعيداً
    t = Thread(target=run_web)
    t.start()
    
    print("Web server started. Now launching bot.py...")
    
    # 2. محاولة تشغيل البوت مع طباعة أي خطأ قد يحدث بشكل دقيق
    try:
        import bot
    except Exception as e:
        print("❌ Error occurred while starting bot:")
        traceback.print_exc()
