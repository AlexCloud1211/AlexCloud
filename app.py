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
sent_users = set()  # Lưu user đã được gửi tin nhắn

# ===== SỰ KIỆN NHẬN TIN NHẮN =====
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if not event.is_private or event.out:
        return
    
    user_id = event.sender_id
    
    # KIỂM TRA 1: User đã được gửi tin nhắn chưa?
    if user_id in sent_users:
        print(f"⏭️ Bỏ qua user {user_id} - đã gửi trước đó")
        return
    
    # KIỂM TRA 2: Có đang offline không?
    if is_online:
        print(f"⏭️ Bỏ qua user {user_id} - đang online")
        return
    
    # Nếu đã offline và chưa gửi -> tiến hành gửi
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
        
        # Đánh dấu user đã được gửi
        sent_users.add(user_id)
        
        print(f"✅ Đã gửi 2 tin nhắn cho {sender_name} (ID: {user_id}) lúc {time.ctime()}")
        print(f"📊 Đã gửi cho {len(sent_users)} user khác nhau")
        
    except Exception as e:
        print(f"❌ Lỗi khi gửi cho user {user_id}: {e}")

# Khi bạn gửi tin nhắn -> online + reset sent_users (tùy chọn)
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
                print(f"💡 Bot sẽ bắt đầu gửi tin nhắn khi có người nhắn (mỗi user 1 lần)")
            is_online = False
        else:
            if not is_online:
                print(f"🟢 Online - {time.ctime()}")
                print(f"📊 Đã gửi cho {len(sent_users)} user")
            is_online = True
        await asyncio.sleep(10)

# Reset danh sách đã gửi khi online (tùy chọn - bỏ comment nếu muốn)
# @client.on(events.NewMessage(outgoing=True))
# async def reset_sent_users(event):
#     global sent_users
#     if sent_users:
#         sent_users.clear()
#         print(f"🔄 Đã reset danh sách user đã gửi")

async def run_telegram_bot():
    try:
        if SESSION_STRING:
            await client.connect()
