from flask import Flask
from telethon import TelegramClient, events, sessions
import asyncio
import os
import threading
import time

# ===== THIẾT LẬP BIẾN MÔI TRƯỜNG =====
API_ID = int(os.environ.get('API_ID', 34047859))
API_HASH = os.environ.get('API_HASH', '8f96da8891018b8ddbb2b5eefc562c93')
PHONE = os.environ.get('PHONE', '+84904696471')
SESSION_STRING = os.environ.get('SESSION_STRING', None)

# ===== CẤU HÌNH BOT =====
ONLINE_TIMEOUT = 10

# ===== ẢNH CHUYỂN KHOẢN (Dùng URL) =====
IMAGE_URL = "https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg"

# ===== NỘI DUNG TIN NHẮN DUY NHẤT =====
AUTO_REPLY = "CẦN GÌ CỨ BANK GỬI BILL ZEN SẼ REP SAU ÍT PHÚT"

# ===== KHỞI TẠO FLASK APP =====
app = Flask(__name__)

# ===== KHỞI TẠO TELEGRAM CLIENT =====
if SESSION_STRING:
    client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("🔐 Đang dùng Session String để đăng nhập...")
else:
    client = TelegramClient('session_hc', API_ID, API_HASH)
    print("🔐 Đang dùng Session File + OTP để đăng nhập...")

is_online = True
last_activity = time.time()

# ===== SỰ KIỆN NHẬN TIN NHẮN - GỬI ẢNH + NỘI DUNG =====
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if not event.is_private or event.out:
        return
    
    if not is_online:
        try:
            sender = await event.get_sender()
            sender_name = sender.first_name or sender.username or str(event.sender_id)
            
            # Gửi ảnh (URL) + nội dung (KHÔNG reply)
            await client.send_file(
                entity=event.sender_id,
                file=IMAGE_URL,
                caption=AUTO_REPLY
            )
            
            print(f"✅ Đã gửi ảnh + nội dung cho {sender_name} lúc {time.ctime()}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")

# Khi bạn gửi tin nhắn -> online
@client.on(events.NewMessage(outgoing=True))
async def set_online(event):
    global is_online, last_activity
    is_online = True
    last_activity = time.time()
    print(f"🟢 Online - {time.ctime()}")

# Cập nhật online khi đọc tin nhắn
@client.on(events.MessageRead)
async def set_online_read(event):
    global is_online, last_activity
    is_online = True
    last_activity = time.time()

async def check_online_status():
    global is_online, last_activity
    while True:
        if time.time() - last_activity > ONLINE_TIMEOUT:
            if is_online:
                print(f"🔴 Offline - {time.ctime()}")
            is_online = False
        else:
            if not is_online:
                print(f"🟢 Online - {time.ctime()}")
                is_online = True
        await asyncio.sleep(5)

async def run_telegram_bot():
    try:
        if SESSION_STRING:
            await client.connect()
            if not await client.is_user_authorized():
                print("❌ Session String không hợp lệ!")
                return
        else:
            await client.start(phone=PHONE)
        
        me = await client.get_me()
        print(f"🚀 Bot chạy với tài khoản: {me.first_name} (@{me.username})")
        print(f"📱 Số điện thoại: {PHONE}")
        print(f"⏰ Timeout offline: {ONLINE_TIMEOUT} giây")
        print("📨 Đang theo dõi tin nhắn...\n")
        
        asyncio.create_task(check_online_status())
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Lỗi bot Telegram: {e}")

@app.route('/')
def health_check():
    return "🤖 Bot is running!", 200

@app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

@app.route('/status')
def status():
    status_text = "🟢 Online" if is_online else "🔴 Offline"
    return f"Bot status: {status_text}", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    telethon_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    telethon_thread.daemon = True
    telethon_thread.start()
    print(f"🔄 Đang khởi động Flask server...")
    run_flask()
