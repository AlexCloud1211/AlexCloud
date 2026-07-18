from flask import Flask, request
from telethon import TelegramClient, events, sessions
import asyncio
import os
import threading
import time

# ===== THIẾT LẬP BIẾN MÔI TRƯỜNG =====
API_ID = int(os.environ.get('API_ID', 34047859))
API_HASH = os.environ.get('API_HASH', '8f96da8891018b8ddbb2b5eefc562c93')
PHONE = os.environ.get('PHONE', '+84904696471')
LOGIN_CODE = os.environ.get('LOGIN_CODE', None)  # Mã OTP dùng 1 lần
SESSION_STRING = os.environ.get('SESSION_STRING', None)  # Session string bền vững

# ===== CẤU HÌNH BOT =====
AUTO_REPLY = "Tôi đang offline, sẽ trả lời bạn sau! ❤️"
ONLINE_TIMEOUT = 10  # 10 giây không hoạt động -> offline

# ===== KHỞI TẠO FLASK APP =====
app = Flask(__name__)

# ===== KHỞI TẠO TELEGRAM CLIENT =====
if SESSION_STRING:
    # Dùng session string (bền vững, không cần OTP mỗi lần)
    client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("🔐 Đang dùng Session String để đăng nhập...")
else:
    # Dùng session file + OTP
    client = TelegramClient('session_hc', API_ID, API_HASH)
    print("🔐 Đang dùng Session File + OTP để đăng nhập...")

# Biến lưu trạng thái online
is_online = True
last_activity = time.time()

# ===== SỰ KIỆN TỰ ĐỘNG REPLY =====
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    # Chỉ xử lý tin nhắn riêng tư
    if not event.is_private:
        return
    
    # Bỏ qua tin nhắn của chính mình
    if event.out:
        return
    
    # Chỉ reply khi đang offline
    if not is_online:
        try:
            await event.reply(AUTO_REPLY)
            print(f"🤖 Đã reply offline cho user {event.sender_id} lúc {time.ctime()}")
        except Exception as e:
            print(f"❌ Lỗi khi reply: {e}")

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

# ===== KIỂM TRA TRẠNG THÁI ONLINE/OFFLINE =====
async def check_online_status():
    global is_online, last_activity
    
    while True:
        # Nếu không có hoạt động trong ONLINE_TIMEOUT giây -> offline
        if time.time() - last_activity > ONLINE_TIMEOUT:
            if is_online:  # Chỉ in 1 lần khi chuyển sang offline
                print(f"🔴 Offline - {time.ctime()}")
            is_online = False
        else:
            if not is_online:
                print(f"🟢 Online - {time.ctime()}")
                is_online = True
        
        await asyncio.sleep(5)

# ===== CHẠY TELEGRAM BOT =====
async def run_telegram_bot():
    try:
        # Đăng nhập với các phương thức khác nhau
        if SESSION_STRING:
            # Đã có session string, chỉ cần kết nối
            await client.connect()
            if not await client.is_user_authorized():
                print("❌ Session String không hợp lệ!")
                return
        elif LOGIN_CODE:
            # Dùng mã OTP từ biến môi trường
            await client.start(phone=PHONE, code_callback=lambda: LOGIN_CODE)
        else:
            # Dùng session file + OTP nhập thủ công (chỉ dùng trên máy tính)
            await client.start(phone=PHONE)
        
        me = await client.get_me()
        print(f"🚀 Bot chạy với tài khoản: {me.first_name} (@{me.username})")
        print(f"📱 Số điện thoại: {PHONE}")
        print(f"⏰ Timeout offline: {ONLINE_TIMEOUT} giây")
        print("📨 Đang chờ tin nhắn...\n")
        
        # Chạy kiểm tra trạng thái song song
        asyncio.create_task(check_online_status())
        
        # Giữ bot chạy liên tục
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Lỗi bot Telegram: {e}")

# ===== FLASK ROUTE =====
@app.route('/')
def health_check():
    return "🤖 Bot is running!", 200

@app.route('/ping')
def ping():
    """Endpoint để ping giữ bot không ngủ"""
    return "Pong! Bot is alive!", 200

@app.route('/status')
def status():
    """Kiểm tra trạng thái bot"""
    status_text = "🟢 Online" if is_online else "🔴 Offline"
    return f"Bot status: {status_text}", 200

# ===== HÀM CHẠY FLASK =====
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ===== MAIN =====
if __name__ == '__main__':
    # Tạo thread riêng cho Telegram bot
    telethon_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    telethon_thread.daemon = True
    telethon_thread.start()
    
    # Chạy Flask app ở main thread
    print(f"🔄 Đang khởi động Flask server...")
    run_flask()
