from flask import Flask, render_template_string, request, redirect
import random, string, time, requests
from datetime import datetime

app = Flask(__name__)

# --- CẤU HÌNH ---
LINK4M_API = "6a27be48f348053ba11f3502"
ADMIN_PIN = "121113"
all_keys = []
GAMES = ["FREE FIRE MAX", "FREE FIRE"]
DURATIONS = ["12 Giờ", "1 Ngày"]

CSS = """
<style>
    @keyframes bgChange { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
    @keyframes colorChange { 0%{color: #ff0000;} 20%{color: #ff8000;} 40%{color: #ffff00;} 60%{color: #00ff00;} 80%{color: #0000ff;} 100%{color: #ff0000;} }
    
    body { 
        background: linear-gradient(-45deg, #ff0000, #ff8000, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); 
        background-size: 400% 400%; 
        animation: bgChange 10s ease infinite; 
        font-family: 'Segoe UI', sans-serif; 
        display: flex; flex-direction: column; align-items: center; min-height: 100vh; margin: 0; padding: 20px; 
    }
    
    .card { 
        background: rgba(255,255,255,0.98); 
        padding: 40px; border-radius: 25px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.4); 
        width: 90%; max-width: 450px; text-align: center; 
    }
    
    h1 { font-size: 2.8rem; animation: colorChange 4s infinite; font-weight: 800; margin-bottom: 20px; }
    
    .btn { 
        background: #000; color: #fff; padding: 18px; border-radius: 12px; 
        cursor: pointer; font-size: 1.4rem; font-weight: bold; width: 100%; 
        border: none; margin-top: 25px; transition: 0.3s;
    }
    .btn:hover { transform: scale(1.02); background: #222; }

    select { 
        font-size: 1.1rem; padding: 12px; width: 100%; margin-top: 15px; 
        border-radius: 10px; border: 2px solid #eee; outline: none; background: #fff;
    }

    .info-text { font-size: 1.1rem; margin-top: 15px; color: #555; }
    
    footer { margin-top: auto; padding: 20px; }
    .footer-link { color: #fff; text-decoration: none; font-size: 0.9rem; font-weight: bold; text-shadow: 1px 1px 3px #000; }

    table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; font-size: 0.7rem; border-radius: 10px; overflow: hidden; }
    th, td { border: 1px solid #eee; padding: 8px; text-align: center; }
    th { background: #000; color: #fff; }
</style>
"""

def get_html(content):
    return f"""<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>{CSS}</head>
    <body onclick="document.getElementById('bgMusic').play()">
    <audio id="bgMusic" loop autoplay><source src='https://files.catbox.moe/5rqwul.mp3' type='audio/mpeg'></audio>
    <script>window.onload = function() {{ document.getElementById('bgMusic').play(); }}</script>
    <div class='card'>{content}</div>
    <footer><a href='/admin-login' class='footer-link'>@2026 AlexCloud</a></footer></body></html>"""

@app.route('/')
def home():
    game_opts = "".join([f"<option value='{g}'>{g}</option>" for g in GAMES])
    time_opts = "".join([f"<option value='{d}'>{d}</option>" for d in DURATIONS])
    content = f"""
    <h1>AlexCloud Cheat</h1>
    <label>Chọn Game:</label>
    <select id='game'>{game_opts}</select>
    <label style='display:block; margin-top:15px;'>Chọn Thời Hạn:</label>
    <select id='duration'>{time_opts}</select>
    <p class='info-text'>Cấu hình: <b>1 Thiết Bị</b></p>
    <button class='btn' onclick="window.location.href='/get-key?game='+document.getElementById('game').value+'&dur='+document.getElementById('duration').value">NHẬN KEY</button>
    """
    return render_template_string(get_html(content))

@app.route('/get-key')
def get_key():
    game = request.args.get('game', 'FREE FIRE MAX')
    dur = request.args.get('dur', '1 Ngày')
    k = f"AlexCloud-{''.join(random.choices(string.ascii_uppercase, k=3))}-{''.join(random.choices(string.digits, k=3))}"
    all_keys.append({'key': k, 'game': game, 'dev': '1', 'exp': dur, 'time': datetime.now().strftime("%H:%M:%S")})
    
    url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API}&url=https://alexcloud-ukf8.onrender.com/verify?key={k}&dur={dur}"
    try: return redirect(requests.get(url).json()['shortenedUrl'])
    except: return "Lỗi API!"

@app.route('/verify')
def verify():
    k = request.args.get('key')
    dur = request.args.get('dur', '1 Ngày')
    js = f"""<script>
        function copy(){{
            navigator.clipboard.writeText('{k}');
            let b = document.getElementById('cpBtn');
            b.innerText = 'ĐÃ COPY THÀNH CÔNG!';
            b.style.background = '#28a745';
            setTimeout(()=>{{ b.innerText = 'NHẬN LẠI KEY'; b.style.background = '#000'; }}, 2000);
        }}
    </script>"""
    return render_template_string(get_html(f"{js}<h1>KEY CỦA BẠN:</h1><h1 style='color:red'>{k}</h1><p>Thời hạn: <b>{dur}</b></p><button id='cpBtn' class='btn' onclick='copy()'>NHẤN ĐỂ COPY</button><br><br><a href='/'>Về trang chủ</a>"))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('pin') == ADMIN_PIN:
            if 'create' in request.form:
                all_keys.append({'key': f"AlexCloud-{''.join(random.choices(string.ascii_uppercase, k=3))}-{''.join(random.choices(string.digits, k=3))}", 'game': request.form.get('game'), 'dev': request.form.get('dev'), 'exp': request.form.get('time'), 'time': datetime.now().strftime("%H:%M:%S")})
            rows = "".join([f"<tr><td>{i['key']}</td><td>{i['game']}</td><td>{i['dev']}</td><td>{i['exp']}</td><td>{i['time']}</td></tr>" for i in all_keys])
            return render_template_string(get_html(f"<h1>ADMIN</h1><form method='POST'><input type='hidden' name='pin' value='{ADMIN_PIN}'>Game: <select name='game'>{''.join([f'<option>{g}</option>' for g in GAMES])}</select><br>TBI: <input name='dev' value='1' style='width:30px'> Hạn: <select name='time'><option value='12 Giờ'>12 Giờ</option><option value='1 Ngày'>1 Ngày</option></select><button name='create' value='1' class='btn' style='font-size:1rem'>TẠO KEY</button></form><table><tr><th>KEY</th><th>GAME</th><th>TBI</th><th>HẠN</th><th>LÚC TẠO</th></tr>{rows}</table><br><a href='/' class='btn' style='font-size:1rem'>THOÁT</a>"))
    return render_template_string(get_html("<h1>NHẬP PIN</h1><form method='POST'><input name='pin' type='password' style='padding:15px; width:80%; border-radius:10px; border:1px solid #eee;'><br><button class='btn'>XÁC NHẬN</button></form>"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
