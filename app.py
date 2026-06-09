# -*- coding: utf-8 -*-
import http.server
import socketserver
import random
import string
import time
from urllib.parse import urlparse, parse_qs

# --- CẤU HÌNH ---
PORT = 8080
ADMIN_USER = "Admin"
ADMIN_PASS = "Longyy1211"
ADMIN_PIN = "121113"
all_keys = [] 

def gen_key():
    l = ''.join(random.choices(string.ascii_uppercase, k=3))
    n = ''.join(random.choices(string.digits, k=3))
    return f"AlexCloud-{l}-{n}"

CSS = """
<style>
    body { background: #000; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
    .btn { padding: 10px 20px; border-radius: 5px; border: none; background: #fff; color: #000; font-weight: bold; cursor: pointer; margin: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #444; padding: 8px; text-align: center; font-size: 0.8rem; }
    input, select { padding: 5px; margin: 5px; }
    footer { margin-top: auto; padding: 20px; font-size: 0.8rem; color: #555; }
</style>
"""

def get_html(body):
    return f"""<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>{CSS}</head><body>
    <audio autoplay loop><source src='https://files.catbox.moe/5rqwul.mp3' type='audio/mpeg'></audio>
    <div style='display:flex; flex-direction:column; align-items:center; width:100%;'>{body}</div>
    <footer><a href='/admin-panel' style='color:#555; text-decoration:none;'>@2026 - AlexCloud</a></footer>
    </body></html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global all_keys
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        u, p, pin = params.get('u', [''])[0], params.get('p', [''])[0], params.get('pin', [''])[0]
        
        if path == '/admin-panel':
            if u != ADMIN_USER or p != ADMIN_PASS or pin != ADMIN_PIN:
                form = "<h1>ĐĂNG NHẬP</h1><form action='/admin-panel'>User: <input type='text' name='u'><br>Pass: <input type='password' name='p'><br>PIN: <input type='password' name='pin'><br><button class='btn'>ĐĂNG NHẬP</button></form>"
                self.send_response(200); self.end_headers(); self.wfile.write(get_html(form).encode('utf-8'))
                return
            
            rows = "".join([f"<tr><td>{i['key']}</td><td>{i['dev']}</td><td>{i['t']}</td><td>{i['time']}</td><td><a href='/delete?id={i['id']}&u={u}&p={p}&pin={pin}' style='color:red'>XÓA</a></td></tr>" for i in all_keys])
            ui = f"<h1>QUẢN TRỊ</h1><form action='/create-key'><input type='hidden' name='u' value='{u}'><input type='hidden' name='p' value='{p}'><input type='hidden' name='pin' value='{pin}'>ĐV: <input type='number' name='d' value='1' style='width:40px'> Hạn: <select name='t'><option value='12h'>12h</option><option value='24h'>24h</option></select> <button class='btn'>TẠO</button></form><table><tr><th>KEY</th><th>ĐV</th><th>HẠN</th><th>LÚC</th><th>XÓA</th></tr>{rows}</table><br><a href='/' style='color:#fff'>THOÁT</a>"
            self.send_response(200); self.end_headers(); self.wfile.write(get_html(ui).encode('utf-8'))

        elif path == '/':
            ui = "<h1>AlexCloud</h1><button class='btn' onclick='location.href=\"/get-key\"'>LẤY KEY</button>"
            self.send_response(200); self.end_headers(); self.wfile.write(get_html(ui).encode('utf-8'))
        elif path == '/get-key':
            k = gen_key()
            now = time.strftime("%H:%M:%S")
            all_keys.append({'id': len(all_keys)+1, 'key': k, 'dev': '1', 't': '12h', 'time': now})
            ui = f"<h1>KEY CỦA BẠN:</h1><h1 style='color:yellow'>{k}</h1><p>Tạo lúc: {now}</p><br><button class='btn' onclick='location.href=\"/\"'>QUAY LẠI</button>"
            self.send_response(200); self.end_headers(); self.wfile.write(get_html(ui).encode('utf-8'))
        elif path == '/create-key':
            all_keys.append({'id': len(all_keys)+1, 'key': gen_key(), 'dev': params.get('d', ['1'])[0], 't': params.get('t', ['12h'])[0], 'time': time.strftime("%H:%M:%S")})
            self.send_response(302); self.send_header('Location', f'/admin-panel?u={u}&p={p}&pin={pin}'); self.end_headers()
        elif path == '/delete':
            id_to_del = int(params.get('id', [0])[0])
            all_keys = [i for i in all_keys if i['id'] != id_to_del]
            self.send_response(302); self.send_header('Location', f'/admin-panel?u={u}&p={p}&pin={pin}'); self.end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.allow_reuse_address = True
    print(f"Server chạy tại: http://localhost:{PORT}")
    httpd.serve_forever()