from flask import Flask
from telethon import TelegramClient, events, sessions
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

# Bot Token
BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', 7463456773))

# ===== CẤU HÌNH BOT =====
ONLINE_TIMEOUT = 60
COOLDOWN_TIME = 600

# ===== ẢNH =====
IMAGE_URL = "https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg"
WELCOME_IMAGE_URL = "https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg"

# ===== NỘI DUNG =====
MESSAGE_1 = """HIỆN TẠI BẠN ZEN ĐANG BẬN ❌
CHÀO BẠN ĐÃ ĐẾN VỚI ZENMODS ✅
CÓ VIỆC GÌ THÌ CỨ NHẮN NHÉ 🛒
━━━━━━━━━━━━
GROUP ZEN Ở ĐÂY NÈ: https://t.me/ZenStoreVn 👑
CẢM ƠN BẠN ĐÃ ỦNG HỘ. 😀
NÀO ZEN ONLINE SẼ REPLY BẠN"""

MESSAGE_2 = "CẦN GÌ CỨ BANK ZEN THÍCH LẮM =))"

WELCOME_MESSAGE = """🌧 #Chào Mừng <b>{user_name}</b> Đến Với Group ZenMods nơi của các nhà vua 💤

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

LEAVE_MESSAGE = """😢 <b>{user_name}</b> ĐÃ RỜI NHÓM!

━━━━━━━━━━━━
📌 Rời đi 1 thành viên
👥 Số thành viên còn lại: {members}
━━━━━━━━━━━━

💔 LẠI 1 THẰNG NỮA ĐÃ CÚC KHỎI NHÓM!"""

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
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# Biến lưu trạng thái
is_online = True
last_activity = time.time()
sent_users = {}

# ============================================
# PHẦN 1: USER CLIENT (PREMIUM FAKE)
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
# PHẦN 2: BOT CLIENT (LỆNH ẨN)
# ============================================

@bot_client.on(events.ChatAction)
async def handle_group_events(event):
    try:
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        try:
            participants = await bot_client.get_participants(chat)
            member_count = len(participants)
        except:
            member_count = "???"
        
        if event.user_joined or event.added_by:
            new_user = event.user
            first_name = new_user.first_name or "Người dùng"
            username = new_user.username or "Không có username"
            user_id = new_user.id
            
            welcome_text = WELCOME_MESSAGE.format(
                user_name=first_name,
                members=member_count,
                username=f"@{username}" if username != "Không có username" else username,
                user_id=user_id
            )
            
            await bot_client.send_file(
                chat_id,
                file=WELCOME_IMAGE_URL,
                caption=welcome_text,
                parse_mode='html'
            )
            print(f"🎉 [Bot] Đã chào mừng {first_name}")
        
        if event.user_left:
            left_user = event.user
            first_name = left_user.first_name or "Người dùng"
            
            leave_text = LEAVE_MESSAGE.format(
                user_name=first_name,
                members=member_count
            )
            
            await bot_client.send_file(
                chat_id,
                file=WELCOME_IMAGE_URL,
                caption=leave_text,
                parse_mode='html'
            )
            print(f"😢 [Bot] {first_name} đã rời nhóm")
        
    except Exception as e:
        print(f"❌ Lỗi xử lý group: {e}")

# ============================================
# LỆNH ẨN: /check (CHỈ BẠN BIẾT)
# ============================================

@bot_client.on(events.NewMessage(pattern='/check'))
async def check_command(event):
    """Lệnh /check - Kiểm tra kết nối bot (ẩn)"""
    # Chỉ cho phép user ID của bạn
    if event.sender_id != YOUR_USER_ID:
        # Không trả lời gì, giữ bí mật
        return
    
    try:
        # Kiểm tra User Client
        user_me = await user_client.get_me()
        user_status = "🟢 Kết nối tốt" if user_me else "🔴 Lỗi"
        
        # Kiểm tra Bot Client
        bot_me = await bot_client.get_me()
        bot_status = "🟢 Kết nối tốt" if bot_me else "🔴 Lỗi"
        
        # Kiểm tra session
        session_status = "✅ Có session" if SESSION_STRING else "❌ Không có session (dùng OTP)"
        
        # Tạo tin nhắn báo cáo
        report = f"""🔍 <b>KIỂM TRA KẾT NỐI BOT</b>

━━━━━━━━━━━━━━━━━━
📱 <b>User Client:</b> {user_status}
👤 Tên: {user_me.first_name if user_me else '❌'}
🆔 ID: {user_me.id if user_me else '❌'}

━━━━━━━━━━━━━━━━━━
🤖 <b>Bot Client:</b> {bot_status}
👤 Tên: {bot_me.first_name if bot_me else '❌'}
🆔 ID: {bot_me.id if bot_me else '❌'}

━━━━━━━━━━━━━━━━━━
🔐 <b>Session:</b> {session_status}
📶 <b>Trạng thái:</b> {'🟢 Online' if is_online else '🔴 Offline'}
👥 <b>Đã gửi auto-reply:</b> {len(sent_users)} user
⏰ <b>Cooldown:</b> {COOLDOWN_TIME/60} phút

━━━━━━━━━━━━━━━━━━
✅ Bot đang hoạt động bình thường!"""
        
        # Gửi tin nhắn riêng cho bạn (ẩn, không reply)
        await bot_client.send_message(
            YOUR_USER_ID,
            report,
            parse_mode='html'
        )
        
        # Không trả lời trong chat, giữ bí mật
        print(f"🔍 Đã gửi báo cáo /check cho bạn")
        
    except Exception as e:
        await bot_client.send_message(
            YOUR_USER_ID,
            f"❌ Lỗi kiểm tra: {e}"
        )
        print(f"❌ Lỗi /check: {e}")

# ============================================
# LỆNH ẨN: /gui [id] [nội dung] - GỬI TIN NHẮN
# ============================================

@bot_client.on(events.NewMessage(pattern='/gui'))
async def gui_command(event):
    """Lệnh /gui <id> <nội dung> - Gửi tin nhắn từ user client"""
    # Chỉ cho phép user ID của bạn
    if event.sender_id != YOUR_USER_ID:
        return
    
    try:
        # Lấy nội dung lệnh
        full_text = event.raw_text
        parts = full_text.split(' ', 2)  # Tối đa 3 phần: /gui, id, nội dung
        
        if len(parts) < 3:
            await bot_client.send_message(
                YOUR_USER_ID,
                "⚠️ <b>Cách dùng:</b>\n/gui [user_id] [nội dung tin nhắn]\n\nVí dụ:\n/gui 123456789 Xin chào!",
                parse_mode='html'
            )
            return
        
        target_id = int(parts[1])
        message_content = parts[2]
        
        # Gửi tin nhắn từ User Client
        await user_client.send_message(
            entity=target_id,
            message=message_content
        )
        
        # Thông báo thành công
        await bot_client.send_message(
            YOUR_USER_ID,
            f"✅ <b>Đã gửi tin nhắn thành công!</b>\n"
            f"📤 Đến ID: <code>{target_id}</code>\n"
            f"💬 Nội dung: {message_content}",
            parse_mode='html'
        )
        
        print(f"📤 Đã gửi tin nhắn từ User Client đến {target_id}")
        
    except ValueError:
        await bot_client.send_message(
            YOUR_USER_ID,
            "❌ ID không hợp lệ! Vui lòng nhập số ID.",
            parse_mode='html'
        )
    except Exception as e:
        await bot_client.send_message(
            YOUR_USER_ID,
            f"❌ Lỗi gửi tin nhắn: {e}",
            parse_mode='html'
        )
        print(f"❌ Lỗi /gui: {e}")

# ============================================
# LỆNH CŨ (VẪN GIỮ) - KHÔNG CÒN /START
# ============================================

@bot_client.on(events.NewMessage(pattern='/ping'))
async def ping_command(event):
    """Lệnh /ping - Kiểm tra bot còn sống"""
    await event.reply("🏓 <b>Pong!</b> Bot đang hoạt động bình thường!", parse_mode='html')

@bot_client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    """Lệnh /status - Xem trạng thái"""
    status_text = "🟢 Online" if is_online else "🔴 Offline"
    await event.reply(
        f"📊 <b>Trạng thái bot:</b>\n"
        f"• User trạng thái: {status_text}\n"
        f"• Đã gửi auto-reply: {len(sent_users)} user\n"
        f"• Cooldown: {COOLDOWN_TIME/60} phút",
        parse_mode='html'
    )

@bot_client.on(events.NewMessage(pattern='/stats'))
async def stats_command(event):
    """Lệnh /stats - Thống kê"""
    await event.reply(
        f"📈 <b>Thống kê:</b>\n"
        f"👥 Đã gửi auto-reply: {len(sent_users)} user\n"
        f"📶 Trạng thái: {'🟢 Online' if is_online else '🔴 Offline'}",
        parse_mode='html'
    )

# ============================================
# KHỞI CHẠY
# ============================================

async def run_telegram_bot():
    try:
        # Khởi động Bot Client
        await bot_client.start(bot_token=BOT_TOKEN)
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
        print("🔍 Lệnh ẩn:")
        print("   /check - Kiểm tra kết nối bot")
        print("   /gui <id> <nội dung> - Gửi tin nhắn từ user client")
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
    
    time.sleep(3)
    print("🔄 Đang khởi động Flask server...")
    run_flask()
