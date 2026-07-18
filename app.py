from flask import Flask
from telethon import TelegramClient, events, sessions
from telethon.errors import FloodWaitError
import asyncio
import os
import threading
import time
import random
import logging

# ===== TẮT LOG KHÔNG CẦN THIẾT =====
logging.getLogger('telethon').setLevel(logging.WARNING)

# ===== THIẾT LẬP BIẾN MÔI TRƯỜNG =====
API_ID = int(os.environ.get('API_ID', 34047859))
API_HASH = os.environ.get('API_HASH', '8f96da8891018b8ddbb2b5eefc562c93')
PHONE = os.environ.get('PHONE', '+84904696471')
SESSION_STRING = os.environ.get('SESSION_STRING', None)

# Bot Token
BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
YOUR_USER_ID = int(os.environ.get('YOUR_USER_ID', 7463456773))

# ===== CẤU HÌNH BOT =====
ONLINE_TIMEOUT = 60  # 1 phút
COOLDOWN_TIME = 600  # 10 phút

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
print("🔐 Đang kết nối User Client (acc cá nhân)...")

if SESSION_STRING:
    user_client = TelegramClient(sessions.StringSession(SESSION_STRING), API_ID, API_HASH)
    print("✅ Dùng Session String để đăng nhập...")
else:
    user_client = TelegramClient('session_hc', API_ID, API_HASH)
    print("⚠️ Không có Session String, sẽ dùng OTP...")

# ===== KHỞI TẠO BOT CLIENT =====
print("🤖 Đang kết nối Bot Client...")
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# ===== BIẾN TOÀN CỤC =====
is_online = True
last_activity = time.time()
sent_users = {}  # {user_id: last_sent_time}
user_ready = False
bot_ready = False
start_time = time.time()

# ============================================
# PHẦN 1: USER CLIENT (PREMIUM FAKE)
# ============================================

@user_client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    """Tự động reply khi bạn offline (Premium Fake)"""
    global is_online, user_ready
    
    if not user_ready:
        return
    
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
        
    except FloodWaitError as e:
        print(f"⏳ FloodWait: {e.seconds}s - Đợi rồi thử lại")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"❌ Lỗi auto-reply: {e}")

@user_client.on(events.NewMessage(outgoing=True))
async def set_online_outgoing(event):
    global is_online, last_activity
    if user_ready:
        is_online = True
        last_activity = time.time()

@user_client.on(events.MessageRead)
async def set_online_read(event):
    global is_online, last_activity
    if user_ready:
        is_online = True
        last_activity = time.time()

async def check_online_status():
    """Kiểm tra trạng thái online/offline"""
    global is_online, last_activity, user_ready
    while True:
        if user_ready:
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
# PHẦN 2: BOT CLIENT
# ============================================

@bot_client.on(events.ChatAction)
async def handle_group_events(event):
    """Xử lý sự kiện group: join/leave"""
    global bot_ready
    
    if not bot_ready:
        return
    
    try:
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        try:
            participants = await bot_client.get_participants(chat)
            member_count = len(participants)
        except:
            member_count = "???"
        
        # Thành viên mới vào
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
        
        # Thành viên rời nhóm
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
# LỆNH /check - ĐÃ FIX HOÀN TOÀN
# ============================================

@bot_client.on(events.NewMessage(pattern='/check'))
async def check_command(event):
    """Lệnh /check - Kiểm tra kết nối bot (chỉ bạn)"""
    # CHỈ CHO PHÉP USER ID CỦA BẠN
    if event.sender_id != YOUR_USER_ID:
        return
    
    try:
        # Lấy thông tin User Client
        user_info = "❌ Chưa kết nối"
        user_name = "❌"
        user_id = "❌"
        if user_ready:
            try:
                me = await user_client.get_me()
                user_info = "🟢 Đã kết nối"
                user_name = me.first_name or "Không có tên"
                user_id = me.id
            except:
                user_info = "🟡 Kết nối nhưng lỗi lấy info"
        
        # Lấy thông tin Bot Client
        bot_info = "❌ Chưa kết nối"
        bot_name = "❌"
        bot_id = "❌"
        if bot_ready:
            try:
                me = await bot_client.get_me()
                bot_info = "🟢 Đã kết nối"
                bot_name = me.first_name or "Không có tên"
                bot_id = me.id
            except:
                bot_info = "🟡 Kết nối nhưng lỗi lấy info"
        
        # Tính uptime
        uptime_seconds = int(time.time() - start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        # Tạo báo cáo
        report = f"""🔍 <b>KIỂM TRA KẾT NỐI BOT</b>

━━━━━━━━━━━━━━━━━━
⏰ <b>Uptime:</b> {uptime_str}

━━━━━━━━━━━━━━━━━━
📱 <b>USER CLIENT (Premium Fake):</b>
• Trạng thái: {user_info}
• Tên: {user_name}
• ID: {user_id}
• Online: {'🟢 Online' if is_online else '🔴 Offline'}
• Đã reply: {len(sent_users)} user
• Cooldown: {COOLDOWN_TIME/60} phút

━━━━━━━━━━━━━━━━━━
🤖 <b>BOT CLIENT:</b>
• Trạng thái: {bot_info}
• Tên: {bot_name}
• ID: {bot_id}

━━━━━━━━━━━━━━━━━━
📊 <b>THÔNG TIN HỆ THỐNG:</b>
• API_ID: {API_ID}
• Phone: {PHONE}
• Session: {'✅ Có' if SESSION_STRING else '❌ Không'}

━━━━━━━━━━━━━━━━━━
✅ Bot đang hoạt động bình thường!"""

        # Gửi báo cáo riêng cho bạn
        await bot_client.send_message(
            YOUR_USER_ID,
            report,
            parse_mode='html'
        )
        print(f"🔍 Đã gửi báo cáo /check cho bạn")
        
    except Exception as e:
        await bot_client.send_message(
            YOUR_USER_ID,
            f"❌ Lỗi kiểm tra: {e}",
            parse_mode='html'
        )
        print(f"❌ Lỗi /check: {e}")

# ============================================
# LỆNH /gui - GỬI TIN NHẮN TỪ USER CLIENT
# ============================================

@bot_client.on(events.NewMessage(pattern='/gui'))
async def gui_command(event):
    """Lệnh /gui <id> <nội dung> - Gửi tin nhắn từ user client"""
    if event.sender_id != YOUR_USER_ID:
        return
    
    if not user_ready:
        await bot_client.send_message(YOUR_USER_ID, "❌ User Client chưa sẵn sàng!")
        return
    
    try:
        parts = event.raw_text.split(' ', 2)
        if len(parts) < 3:
            await bot_client.send_message(
                YOUR_USER_ID,
                "⚠️ <b>Cách dùng:</b>\n/gui [user_id] [nội dung]\n\n<i>Ví dụ:\n/gui 123456789 Xin chào!</i>",
                parse_mode='html'
            )
            return
        
        target_id = int(parts[1])
        message_content = parts[2]
        
        await user_client.send_message(entity=target_id, message=message_content)
        
        await bot_client.send_message(
            YOUR_USER_ID,
            f"✅ <b>Đã gửi tin nhắn thành công!</b>\n📤 Đến ID: <code>{target_id}</code>",
            parse_mode='html'
        )
        print(f"📤 Đã gửi tin nhắn đến {target_id}")
        
    except ValueError:
        await bot_client.send_message(YOUR_USER_ID, "❌ ID không hợp lệ!")
    except Exception as e:
        await bot_client.send_message(YOUR_USER_ID, f"❌ Lỗi: {e}")

# ============================================
# LỆNH CÔNG KHAI
# ============================================

@bot_client.on(events.NewMessage(pattern='/ping'))
async def ping_command(event):
    await event.reply("🏓 <b>Pong!</b> Bot đang hoạt động!", parse_mode='html')

@bot_client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    await event.reply(
        f"📊 <b>Trạng thái:</b>\n"
        f"• User: {'🟢 Online' if is_online else '🔴 Offline'}\n"
        f"• Đã reply: {len(sent_users)} user\n"
        f"• Uptime: {int(time.time() - start_time)//60} phút",
        parse_mode='html'
    )

# ============================================
# KHỞI CHẠY
# ============================================

async def run_telegram_bot():
    global user_ready, bot_ready
    
    try:
        # 1. Kết nối User Client
        print("📱 Đang đăng nhập User Client...")
        if SESSION_STRING:
            await user_client.connect()
            if not await user_client.is_user_authorized():
                print("❌ Session String không hợp lệ!")
                print("💡 Chạy get_session.py để lấy session mới")
                return
        else:
            await user_client.start(phone=PHONE)
        
        user_me = await user_client.get_me()
        print(f"✅ User Client: {user_me.first_name} (@{user_me.username})")
        user_ready = True
        
        # 2. Kết nối Bot Client
        print("🤖 Đang đăng nhập Bot Client...")
        await bot_client.start(bot_token=BOT_TOKEN)
        bot_me = await bot_client.get_me()
        print(f"✅ Bot Client: {bot_me.first_name} (@{bot_me.username})")
        bot_ready = True
        
        # 3. In thông tin
        print("\n" + "="*50)
        print("🚀 ZENMODS BOT ĐÃ KHỞI ĐỘNG!")
        print("="*50)
        print(f"👤 User: {user_me.first_name}")
        print(f"🤖 Bot: {bot_me.first_name}")
        print(f"⏰ Timeout: {ONLINE_TIMEOUT}s | Cooldown: {COOLDOWN_TIME/60}p")
        print("="*50)
        print("🔍 Lệnh ẩn (chỉ bạn):")
        print("   /check - Kiểm tra kết nối chi tiết")
        print("   /gui <id> <nd> - Gửi tin nhắn từ acc bạn")
        print("="*50)
        print("📨 Đang chạy...\n")
        
        # 4. Chạy kiểm tra online
        asyncio.create_task(check_online_status())
        
        # 5. Giữ bot chạy
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
