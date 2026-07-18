from flask import Flask
from telethon import TelegramClient, events, sessions
from telethon.tl.types import MessageEntityTextUrl
import asyncio
import os
import threading
import time
import random

# ===== THIẾT LẬP BIẾN MÔI TRƯỜNG =====
# Thông tin cho User Client (tài khoản cá nhân - Telegram Premium Fake)
API_ID = int(os.environ.get('API_ID', 34047859))
API_HASH = os.environ.get('API_HASH', '8f96da8891018b8ddbb2b5eefc562c93')
PHONE = os.environ.get('PHONE', '+84904696471')
SESSION_STRING = os.environ.get('SESSION_STRING', None)

# Thông tin cho Bot Client (Bot Token từ @BotFather)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw')

# ID Telegram của bạn (để nhận mã test)
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', 7463456773))

# ===== CẤU HÌNH BOT =====
ONLINE_TIMEOUT = 60  # 60 giây = 1 phút
COOLDOWN_TIME = 600  # 600 giây = 10 phút

# ===== ẢNH CHUYỂN KHOẢN =====
IMAGE_URL = "https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg"

# ===== NỘI DUNG AUTO REPLY (Telegram Premium Fake) =====
MESSAGE_1 = """HIỆN TẠI BẠN ZEN ĐANG BẬN ❌
CHÀO BẠN ĐÃ ĐẾN VỚI ZENMODS ✅
CÓ VIỆC GÌ THÌ CỨ NHẮN NHÉ 🛒
━━━━━━━━━━━━
GROUP ZEN Ở ĐÂY NÈ: https://t.me/ZenStoreVn 👑
CẢM ƠN BẠN ĐÃ ỦNG HỘ. 😀
NÀO ZEN ONLINE SẼ REPLY BẠN"""

MESSAGE_2 = "CẦN GÌ CỨ BANK ZEN THÍCH LẮM =))"

# ===== NỘI DUNG WELCOME CHO GROUP =====
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

# ===== KHỞI TẠO USER CLIENT (Telegram Premium Fake) =====
if SESSION_STRING:
    user_client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("🔐 User Client: Đang dùng Session String...")
else:
    user_client = TelegramClient('session_hc', API_ID, API_HASH)
    print("🔐 User Client: Đang dùng Session File...")

# ===== KHỞI TẠO BOT CLIENT (Bot Token) =====
bot_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
print("🤖 Bot Client: Đã đăng nhập với Bot Token!")

# Biến lưu trạng thái
is_online = True
last_activity = time.time()
sent_users = {}  # {user_id: last_sent_time}

# ============================================
# PHẦN 1: USER CLIENT (TELEGRAM PREMIUM FAKE)
# ============================================

@user_client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    """Tự động reply khi bạn offline (giả lập Telegram Premium)"""
    global is_online
    
    if not event.is_private or event.out:
        return
    
    user_id = event.sender_id
    current_time = time.time()
    
    # Kiểm tra offline
    if is_online:
        return
    
    # Kiểm tra cooldown 10 phút
    if user_id in sent_users:
        if current_time - sent_users[user_id] < COOLDOWN_TIME:
            return
    
    try:
        sender = await event.get_sender()
        sender_name = sender.first_name or sender.username or str(user_id)
        
        # Gửi tin nhắn 1 (không ảnh)
        await user_client.send_message(
            entity=user_id,
            message=MESSAGE_1
        )
        
        # Gửi tin nhắn 2 (kèm ảnh)
        await user_client.send_file(
            entity=user_id,
            file=IMAGE_URL,
            caption=MESSAGE_2
        )
        
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
# PHẦN 2: BOT CLIENT (BOT TOKEN)
# ============================================

@bot_client.on(events.ChatAction)
async def welcome_new_member(event):
    """Chào mừng thành viên mới vào group"""
    try:
        if not event.user_joined and not event.added_by:
            return
        
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        # Đếm thành viên
        try:
            participants = await bot_client.get_participants(chat)
            member_count = len(participants)
        except:
            member_count = "???"
        
        # Lấy thông tin thành viên mới
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
        print(f"🎉 [Bot] Đã chào mừng {first_name} vào group")
        
    except Exception as e:
        print(f"❌ Lỗi welcome: {e}")

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    """Lệnh /start"""
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

@bot_client.on(events.NewMessage(pattern='/ping'))
async def ping_command(event):
    """Lệnh /ping"""
    await event.reply("🏓 <b>Pong!</b> Bot đang hoạt động bình thường!", parse_mode='html')

@bot_client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    """Lệnh /status"""
    status_text = "🟢 Online" if is_online else "🔴 Offline"
    await event.reply(
        f"📊 <b>Trạng thái bot:</b>\n"
        f"• User trạng thái: {status_text}\n"
        f"• Đã gửi auto-reply: {len(sent_users)} user\n"
        f"• Cooldown: {COOLDOWN_TIME/60} phút\n"
        f"• Offline timeout: {ONLINE_TIMEOUT} giây",
        parse_mode='html'
    )

@bot_client.on(events.NewMessage(pattern='/getcode'))
async def send_test_code(event):
    """Lệnh /getcode - Gửi mã OTP test về cho bạn"""
    if event.sender_id != YOUR_USER_ID:
        await event.reply("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    otp_code = random.randint(100000, 999999)
    timestamp = time.strftime("%H:%M:%S - %d/%m/%Y")
    
    message = f"""🔐 <b>MÃ XÁC MINH TELEGRAM</b>

━━━━━━━━━━━━━━━━━━
Mã OTP của bạn: <code>{otp_code}</code>
━━━━━━━━━━━━━━━━━━

⏰ Thời gian: {timestamp}
⏳ Hiệu lực: <b>5 phút</b>

<b>⚠️ KHÔNG chia sẻ mã này với bất kỳ ai!</b>

━━━━━━━━━━━━━━━━━━
🤖 ZenMods Bot"""
    
    try:
        await bot_client.send_message(YOUR_USER_ID, message, parse_mode='html')
        await event.reply(f"✅ Đã gửi mã OTP <b>{otp_code}</b> về tài khoản của bạn!", parse_mode='html')
        print(f"📤 [Bot] Đã gửi mã OTP: {otp_code}")
    except Exception as e:
        await event.reply(f"❌ Lỗi gửi mã: {e}")

@bot_client.on(events.NewMessage(pattern='/stats'))
async def stats_command(event):
    """Lệnh /stats - Thống kê bot"""
    await event.reply(
        f"📈 <b>Thống kê ZENMODS Bot</b>\n\n"
        f"👥 Đã gửi auto-reply: {len(sent_users)} user\n"
        f"⏱️ Cooldown: {COOLDOWN_TIME/60} phút\n"
        f"📶 Trạng thái: {'🟢 Online' if is_online else '🔴 Offline'}\n"
        f"🤖 Bot Token: Đang hoạt động\n"
        f"👤 User Client: {'✅ Kết nối' if SESSION_STRING else '⚠️ Chưa có session'}",
        parse_mode='html'
    )

# ============================================
# KHỞI CHẠY BOT
# ============================================

async def run_telegram_bot():
    try:
        # Kết nối User Client
        if SESSION_STRING:
            await user_client.connect()
            if not await user_client.is_user_authorized():
                print("❌ Session String không hợp lệ!")
                return
        else:
            await user_client.start(phone=PHONE)
        
        # Lấy thông tin
        me = await user_client.get_me()
        bot_info = await bot_client.get_me()
        
        print("\n" + "="*50)
        print("🚀 ZENMODS BOT ĐÃ KHỞI ĐỘNG!")
        print("="*50)
        print(f"👤 User Client: {me.first_name} (@{me.username})")
        print(f"🤖 Bot Client: {bot_info.first_name} (@{bot_info.username})")
        print(f"📱 Số điện thoại: {PHONE}")
        print(f"⏰ Offline timeout: {ONLINE_TIMEOUT}s")
        print(f"⏰ Cooldown: {COOLDOWN_TIME/60} phút")
        print("="*50)
        print("📨 Đang chạy...\n")
        
        asyncio.create_task(check_online_status())
        await user_client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

@app.route('/')
def health_check():
    return "🤖 ZENMODS Bot is running!", 200

@app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

@app.route('/status')
def status():
    return f"Bot status: {'🟢 Online' if is_online else '🔴 Offline'} | Sent: {len(sent_users)} users"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    bot_thread.daemon = True
    bot_thread.start()
    
    print("🔄 Đang khởi động Flask server...")
    run_flask()
