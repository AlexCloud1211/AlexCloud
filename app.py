from flask import Flask
from telethon import TelegramClient, events, sessions
from telethon.tl.types import MessageEntityTextUrl
import asyncio
import os
import threading
import time
import random

# ===== THIẾT LẬP BIẾN MÔI TRƯỜNG =====
API_ID = int(os.environ.get('API_ID', 34047859))
API_HASH = os.environ.get('API_HASH', '8f96da8891018b8ddbb2b5eefc562c93')
PHONE = os.environ.get('PHONE', '+84904696471')
SESSION_STRING = os.environ.get('SESSION_STRING', None)

# Bot Token (đã fix cứng)
BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', 7463456773))

# ===== CẤU HÌNH BOT =====
ONLINE_TIMEOUT = 60
COOLDOWN_TIME = 600

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

WELCOME_MESSAGE = """🌧 #Chào Mừng Bạn Đến Với Group ZenMods nơi của các nhà vua 💤

-> ( Giao Dịch Mua Bán Hack FreeFire Root , Non root , All Hack Adr or IOS .. ) 🧸

   Member ° : {members} ☔️
   UserName ° : {username} 🌧
   User Uid ° : {user_id}

         ˗ˏˋ𓆩Luật Nhóm𓆪ˎˊ˗  

🌸 - Không Spam Tin Nhắn , Sticker 
🌸 - Cấm buôn bán khi không được admin chấp thuận 
🌸 - Hạn Chế Gửi Những Video , Ảnh 18+ 
🌸 - Hạn Chế Var War Đú Ửa Chửi Nhau
🌸 - Cẩn Trọng Trc Khi Giao Dịch Với Ng Nào Đó 
🌸 - Hãy Trung Gian Khi Mua Bán Và Giao Dịch

#zenmods2009"""

# ===== KHỞI TẠO FLASK APP =====
app = Flask(__name__)

# ===== KHỞI TẠO USER CLIENT =====
if SESSION_STRING:
    user_client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("🔐 User Client: Dùng Session String...")
else:
    user_client = TelegramClient('session_hc', API_ID, API_HASH)
    print("🔐 User Client: Dùng Session File...")

# ===== KHỞI TẠO BOT CLIENT =====
print("🤖 Đang kết nối Bot Token...")
bot_client = TelegramClient('bot_session', API_ID, API_HASH)
print("✅ Bot Client đã sẵn sàng!")

# Biến lưu trạng thái
is_online = True
last_activity = time.time()
sent_users = {}
bot_ready = False

# ============================================
# PHẦN 1: USER CLIENT
# ============================================

@user_client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if not event.is_private or event.out:
        return
    
    user_id = event.sender_id
    current_time = time.time()
    
    if is_online:
        return
    
    if user_id in sent_users:
        if current_time - sent_users[user_id] < COOLDOWN_TIME:
            return
    
    try:
        sender = await event.get_sender()
        sender_name = sender.first_name or sender.username or str(user_id)
        
        await user_client.send_message(entity=user_id, message=MESSAGE_1)
        await user_client.send_file(entity=user_id, file=IMAGE_URL, caption=MESSAGE_2)
        
        sent_users[user_id] = current_time
        print(f"✅ [Premium Fake] Đã gửi reply cho {sender_name}")
        
    except Exception as e:
        print(f"❌ Lỗi auto-reply: {e}")

@user_client.on(events.NewMessage(outgoing=True))
async def set_online_outgoing(event):
    global is_online, last_activity
    is_online = True
    last_activity = time.time()

@user_client.on(events.MessageRead)
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
        await asyncio.sleep(10)

# ============================================
# PHẦN 2: BOT CLIENT (ĐÃ FIX)
# ============================================

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    """Lệnh /start - ĐÃ FIX"""
    try:
        await event.reply(
            "🤖 <b>ZENMODS BOT</b>\n\n"
            "📌 <b>Lệnh có sẵn:</b>\n"
            "/start - Hiển thị tin nhắn này\n"
            "/ping - Kiểm tra bot còn sống\n"
            "/status - Xem trạng thái bot\n"
            "/getcode - Nhận mã OTP test\n"
            "/stats - Thống kê bot\n\n"
            "🔹 <b>Telegram Premium Fake</b> đang hoạt động!\n"
            "Khi bạn offline > 1 phút, bot sẽ tự động reply.",
            parse_mode='html'
        )
        print("✅ Đã reply /start")
    except Exception as e:
        print(f"❌ Lỗi /start: {e}")

@bot_client.on(events.NewMessage(pattern='/ping'))
async def ping_command(event):
    await event.reply("🏓 <b>Pong!</b> Bot đang hoạt động bình thường!", parse_mode='html')

@bot_client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    status_text = "🟢 Online" if is_online else "🔴 Offline"
    await event.reply(
        f"📊 <b>Trạng thái bot:</b>\n"
        f"• User trạng thái: {status_text}\n"
        f"• Đã gửi auto-reply: {len(sent_users)} user\n"
        f"• Cooldown: {COOLDOWN_TIME/60} phút",
        parse_mode='html'
    )

@bot_client.on(events.NewMessage(pattern='/getcode'))
async def send_test_code(event):
    if event.sender_id != YOUR_USER_ID:
        await event.reply("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    otp_code = random.randint(100000, 999999)
    message = f"🔐 Mã OTP của bạn: <code>{otp_code}</code>"
    
    try:
        await bot_client.send_message(YOUR_USER_ID, message, parse_mode='html')
        await event.reply(f"✅ Đã gửi mã OTP <b>{otp_code}</b>", parse_mode='html')
    except Exception as e:
        await event.reply(f"❌ Lỗi: {e}")

@bot_client.on(events.NewMessage(pattern='/stats'))
async def stats_command(event):
    await event.reply(
        f"📈 <b>Thống kê:</b>\n"
        f"👥 Đã gửi auto-reply: {len(sent_users)} user\n"
        f"📶 Trạng thái: {'🟢 Online' if is_online else '🔴 Offline'}",
        parse_mode='html'
    )

@bot_client.on(events.ChatAction)
async def welcome_new_member(event):
    try:
        if not event.user_joined and not event.added_by:
            return
        
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        try:
            participants = await bot_client.get_participants(chat)
            member_count = len(participants)
        except:
            member_count = "???"
        
        new_user = event.user
        username = new_user.username or "Không có username"
        user_id = new_user.id
        first_name = new_user.first_name or "Người dùng"
        
        welcome_text = WELCOME_MESSAGE.format(
            members=member_count,
            username=f"@{username}" if username != "Không có username" else username,
            user_id=user_id
        )
        
        await bot_client.send_message(chat_id, welcome_text)
        print(f"🎉 [Bot] Đã chào mừng {first_name}")
        
    except Exception as e:
        print(f"❌ Lỗi welcome: {e}")

# ============================================
# KHỞI CHẠY
# ============================================

async def run_telegram_bot():
    global bot_ready
    
    try:
        # Khởi động Bot Client
        print("🤖 Đang khởi động Bot Client...")
        await bot_client.start(bot_token=BOT_TOKEN)
        bot_ready = True
        
        # Lấy thông tin bot
        bot_me = await bot_client.get_me()
        print(f"✅ Bot Client: {bot_me.first_name} (@{bot_me.username})")
        
        # Kết nối User Client
        if SESSION_STRING:
            await user_client.connect()
            if not await user_client.is_user_authorized():
                print("❌ Session String không hợp lệ!")
                return
        else:
            await user_client.start(phone=PHONE)
        
        user_me = await user_client.get_me()
        
        print("\n" + "="*50)
        print("🚀 ZENMODS BOT ĐÃ KHỞI ĐỘNG!")
        print("="*50)
        print(f"👤 User Client: {user_me.first_name} (@{user_me.username})")
        print(f"🤖 Bot Client: {bot_me.first_name} (@{bot_me.username})")
        print("="*50)
        print("📨 Đang chạy...\n")
        
        asyncio.create_task(check_online_status())
        await user_client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")

@app.route('/')
def health_check():
    return "🤖 ZENMODS Bot is running!", 200

@app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    bot_thread.daemon = True
    bot_thread.start()
    
    # Đợi bot khởi động
    time.sleep(3)
    
    print("🔄 Đang khởi động Flask server...")
    run_flask()
