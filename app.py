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
ONLINE_TIMEOUT = 60  # 60 giây = 1 phút
COOLDOWN_TIME = 600  # 600 giây = 10 phút

# ===== ẢNH CHUYỂN KHOẢN =====
IMAGE_URL = "https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg"

# ===== NỘI DUNG =====
MESSAGE_1 = """HIỆN TẠI BẠN ZEN ĐANG BẬN ❌
CHÀO BẠN ĐÃ ĐẾN VỚI ZENMODS ✅
CÓ VIỆC GÌ THÌ CỨ NHẮN NHÉ 🛒
━━━━━━━━━━━━
GROUP ZEN Ở ĐÂY NÈ: https://t.me/ZenStoreVn 👑
CẢM ƠN BẠN ĐÃ ỦNG HỘ. 😀
NÀO ZEN ONLINE SẼ REPLY BẠN"""

MESSAGE_2 = "CẦN GÌ CỨ BANK ZEN THÍCH LẮM =))"

# ===== KHỞI TẠO FLASK APP =====
app = Flask(__name__)

# ===== KHỞI TẠO TELEGRAM CLIENT =====
if SESSION_STRING:
    client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("🔐 Đang dùng Session String để đăng nhập...")
else:
    client = TelegramClient('session_hc', API_ID, API_HASH)
    print("🔐 Đang dùng Session File + OTP để đăng nhập...")

# Biến lưu trạng thái
is_online = True
last_activity = time.time()
sent_users = {}  # Lưu {user_id: last_sent_time}

# ===== SỰ KIỆN NHẬN TIN NHẮN =====
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if not event.is_private or event.out:
        return
    
    user_id = event.sender_id
    current_time = time.time()
    
    # KIỂM TRA 1: Có đang offline không?
    if is_online:
        print(f"⏭️ Bỏ qua user {user_id} - đang online")
        return
    
    # KIỂM TRA 2: User đã được gửi tin nhắn trong 10 phút chưa?
    if user_id in sent_users:
        last_sent = sent_users[user_id]
        time_diff = current_time - last_sent
        
        if time_diff < COOLDOWN_TIME:
            remaining = int(COOLDOWN_TIME - time_diff)
            print(f"⏭️ Bỏ qua user {user_id} - đã gửi cách đây {int(time_diff/60)} phút, còn {remaining} giây nữa mới được gửi lại")
            return
        else:
            print(f"🔄 User {user_id} đã qua 10 phút, cho phép gửi lại (vì user vừa nhắn tin mới)")
    
    # Nếu đã offline và (chưa gửi lần nào HOẶC đã qua 10 phút) -> tiến hành gửi
    try:
        sender = await event.get_sender()
        sender_name = sender.first_name or sender.username or str(user_id)
        
        # Gửi tin nhắn 1 (không ảnh)
        await client.send_message(
            entity=user_id,
            message=MESSAGE_1
        )
        
        # Gửi tin nhắn 2 (kèm ảnh)
        await client.send_file(
            entity=user_id,
            file=IMAGE_URL,
            caption=MESSAGE_2
        )
        
        # Cập nhật thời gian gửi cuối cùng
        sent_users[user_id] = current_time
        
        print(f"✅ Đã gửi 2 tin nhắn cho {sender_name} (ID: {user_id}) lúc {time.ctime()}")
        print(f"📊 Đã gửi cho {len(sent_users)} user khác nhau")
        
    except Exception as e:
        print(f"❌ Lỗi khi gửi cho user {user_id}: {e}")

# Khi bạn gửi tin nhắn -> online
@client.on(events.NewMessage(outgoing=True))
async def set_online(event):
    global is_online, last_activity
    is_online = True
    last_activity = time.time()
    print(f"🟢 Online - {time.ctime()}")

# Khi bạn đọc tin nhắn -> online
@client.on(events.MessageRead)
async def set_online_read(event):
    global is_online, last_activity
    is_online = True
    last_activity = time.time()
    print(f"🟢 Online (đọc tin nhắn) - {time.ctime()}")

# Kiểm tra trạng thái online
async def check_online_status():
    global is_online, last_activity
    while True:
        if time.time() - last_activity > ONLINE_TIMEOUT:
            if is_online:
                print(f"🔴 Offline - {time.ctime()}")
                print(f"💡 Bot sẽ bắt đầu gửi tin nhắn khi có người nhắn (mỗi user cách nhau 10 phút)")
            is_online = False
        else:
            if not is_online:
                print(f"🟢 Online - {time.ctime()}")
                print(f"📊 Đã gửi cho {len(sent_users)} user")
            is_online = True
        await asyncio.sleep(10)

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
        print(f"⏰ Cooldown giữa các lần gửi: {COOLDOWN_TIME} giây (10 phút)")
        print("📨 Đang theo dõi tin nhắn...\n")
        print("💡 Bot sẽ gửi tin nhắn khi:")
        print("   1. Bạn OFFLINE > 1 phút")
        print("   2. Có người nhắn tin cho bạn")
        print("   3. User đó chưa được gửi trong 10 phút qua")
        
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
    return f"Bot status: {status_text} (Đã gửi cho {len(sent_users)} user)", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    telethon_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    telethon_thread.daemon = True
    telethon_thread.start()
    print(f"🔄 Đang khởi động Flask server...")
    run_flask()
