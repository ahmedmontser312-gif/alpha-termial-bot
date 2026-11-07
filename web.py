import os
import subprocess
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Monky Bot is active and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # 1. تشغيل سيرفر الويب في الخلفية كـ Thread عادي
    import threading
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Web server running. Now launching bot.py as an independent process...")
    
    # 2. تشغيل البوت كعملية مستقلة تماماً (Process) لضمان عمله جنباً إلى جنب مع السيرفر
    subprocess.Popen(["python", "bot.py"])
