import os
from threading import Thread
from flask import Flask

# 1. إنشاء تطبيق ويب وهمي عشان رندر يرضى وما يدينا خطأ 502
app = Flask('')

@app.route('/')
def home():
    return "Monky Bot is active and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # 2. تشغيل سيرفر الويب الوهمي في الخلفية أولاً
    t = Thread(target=run_web)
    t.start()
    
    # 3. تشغيل ملف البوت الأصلي حقك (bot بدون .py)
    import bot
