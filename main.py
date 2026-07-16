# -*- coding: utf-8 -*-
import os
import re
import time
import subprocess
import xml.etree.ElementTree as ET
import math
import tkinter as tk
from tkinter import messagebox, font

if os.name == 'nt':
    os.system('color')
    # Try the requested 745x900 pixel equivalent layout (93x56). Fall back to safer heights if display resolution/scaling limits it.
    if os.system('mode con cols=93 lines=56') != 0:
        if os.system('mode con cols=93 lines=48') != 0:
            os.system('mode con cols=85 lines=45')

# Rich Colorful CLI Theme
OCEAN_BLUE = "\033[38;5;26m"
LIGHT_BLUE = "\033[38;5;117m"
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RED = '\033[91m'
WHITE = '\033[97m'
ORANGE = '\033[38;5;208m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_banner():
    print(f"{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{YELLOW}{BOLD}                 Android Smart Pattern Recovery v1.1                  {RESET}")
    print(f"{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def print_footer():
    print(f"\n{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{YELLOW}Developed By : Ali Sakkaf{RESET}")
    print(f"{WHITE} Website  : https://alisakkaf.com{RESET}")
    print(f"{WHITE} GitHub   : https://github.com/alisakkaf{RESET}")
    print(f"{WHITE} Facebook : https://www.facebook.com/AliSakkaf.Dev{RESET}")
    print(f"{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def run_adb(command):
    try:
        if isinstance(command, list):
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.stdout.strip()
    except Exception:
        return ""

def format_oneui_version(raw_version):
    if not raw_version or not raw_version.isdigit():
        return raw_version
    version_int = int(raw_version)
    return f"{version_int // 10000}.{(version_int % 10000) // 100}"

def get_device_info():
    info = {
        'brand': run_adb("adb shell getprop ro.product.brand").strip(),
        'manufacturer': run_adb("adb shell getprop ro.product.manufacturer").strip(),
        'model': run_adb("adb shell getprop ro.product.model").strip(),
        'board': run_adb("adb shell getprop ro.hardware").strip(),
        'android': run_adb("adb shell getprop ro.build.version.release").strip(),
        'api_level': run_adb("adb shell getprop ro.build.version.sdk").strip(),
        'security': run_adb("adb shell getprop ro.build.version.security_patch").strip(),
        'usb': run_adb("adb shell getprop sys.usb.config").strip() or run_adb("adb shell getprop sys.usb.state").strip(),
        'crypto_state': run_adb("adb shell getprop ro.crypto.state").strip(),
        'oneui': None,
        'width': 1080,
        'height': 2340,
        'dpi': 'Unknown'
    }
    
    if info['brand'].lower() == 'samsung':
        raw_oneui = run_adb("adb shell getprop ro.build.version.oneui").strip() or run_adb("adb shell getprop ro.build.version.sem").strip()
        info['oneui'] = format_oneui_version(raw_oneui)
    
    wm_size = run_adb("adb shell wm size")
    match_size = re.search(r'(\d+)x(\d+)', wm_size)
    if match_size:
        info['width'], info['height'] = int(match_size.group(1)), int(match_size.group(2))
        
    wm_density = run_adb("adb shell wm density")
    match_dpi = re.search(r'(\d+)', wm_density)
    if match_dpi:
        info['dpi'] = match_dpi.group(1)
        
    return info

def is_before_first_unlock():
    user_dump = run_adb("adb shell dumpsys user")
    return "State: RUNNING_LOCKED" in user_dump

def ensure_screen_ready(width, height, is_retry=False):
    if not is_retry:
        print(f"{CYAN}[+] Powering ON screen and preparing UI...{RESET}")
        run_adb("adb shell input keyevent 26")
        time.sleep(1)
    
    run_adb("adb shell input keyevent 82")
    time.sleep(0.5)
    
    if not is_retry:
        print(f"{CYAN}[+] Swiping up to reveal Pattern Grid...{RESET}")
    mid_x = width // 2
    run_adb(f"adb shell input swipe {mid_x} {int(height*0.9)} {mid_x} {int(height*0.1)} 250")
    time.sleep(2)

def attempt_xml_dump(screen_height):
    print(f"{MAGENTA}[+] [Engine 1] Attempting to Dump UI Hierarchy (XML)...{RESET}")
    run_adb("adb shell rm -f /sdcard/window_dump.xml")
    
    dump_res = run_adb("adb shell uiautomator dump /sdcard/window_dump.xml")
    if "dumped to" not in dump_res.lower():
        print(f"{YELLOW}[-] XML Dump blocked by OS security.{RESET}")
        return None

    run_adb("adb pull /sdcard/window_dump.xml .")
    if not os.path.exists("window_dump.xml"):
        return None

    try:
        tree = ET.parse("window_dump.xml")
        for node in tree.getroot().iter():
            res_id, cls_name = node.get("resource-id", ""), node.get("class", "")
            if "LockPatternView" in res_id or "LockPatternView" in cls_name or "pattern" in res_id.lower():
                bounds_str = node.get("bounds")
                matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                if len(matches) == 2:
                    x1, y1 = map(int, matches[0])
                    x2, y2 = map(int, matches[1])
                    node_height = y2 - y1
                    
                    if node_height > (screen_height * 0.5):
                        print(f"{YELLOW}[*] Skipping parent container bounds {bounds_str}... Searching deeper...{RESET}")
                        continue 
                        
                    print(f"{GREEN}[+] XML Dump Success! True Pattern bounds: {bounds_str}{RESET}")
                    return (x1, y1, x2, y2)
    except Exception:
        pass
    
    return None

def calculate_grid_from_bounds(bounds):
    x1, y1, x2, y2 = bounds
    step_x, step_y = (x2 - x1) // 3, (y2 - y1) // 3
    sx, sy = x1 + (step_x // 2), y1 + (step_y // 2)

    return {
        'A': (sx, sy),              'B': (sx + step_x, sy),              'C': (sx + step_x*2, sy),
        'D': (sx, sy + step_y),     'E': (sx + step_x, sy + step_y),     'F': (sx + step_x*2, sy + step_y),
        'G': (sx, sy + step_y*2),   'H': (sx + step_x, sy + step_y*2),   'I': (sx + step_x*2, sy + step_y*2)
    }

def calculate_samsung_grid(info, bfu_state, shift_y=0.0):
    w, h = info['width'], info['height']
    col_1, col_2, col_3 = int(w * 0.236), int(w * 0.500), int(w * 0.764)
    
    if bfu_state:
        row_1 = int(h * (0.597 + shift_y))
        row_2 = int(h * (0.701 + shift_y))
        row_3 = int(h * (0.805 + shift_y))
    else:
        row_1 = int(h * (0.575 + shift_y))
        row_2 = int(h * (0.690 + shift_y))
        row_3 = int(h * (0.771 + shift_y))
        
    return {
        'A': (col_1, row_1), 'B': (col_2, row_1), 'C': (col_3, row_1),
        'D': (col_1, row_2), 'E': (col_2, row_2), 'F': (col_3, row_2),
        'G': (col_1, row_3), 'H': (col_2, row_3), 'I': (col_3, row_3)
    }

def calculate_universal_grid(info, bfu_state, center_y_ratio, spread_x_ratio=0.264):
    w, h = info['width'], info['height']
    col_2 = w // 2
    dx = int(w * spread_x_ratio)
    dy = dx
    
    col_1 = col_2 - dx
    col_3 = col_2 + dx
    
    center_y = int(h * center_y_ratio)
    if bfu_state:
        center_y += int(h * 0.04)
        
    row_2 = center_y
    row_1 = row_2 - dy
    row_3 = row_2 + dy

    return {
        'A': (col_1, row_1), 'B': (col_2, row_1), 'C': (col_3, row_1),
        'D': (col_1, row_2), 'E': (col_2, row_2), 'F': (col_3, row_2),
        'G': (col_1, row_3), 'H': (col_2, row_3), 'I': (col_3, row_3)
    }

def build_attack_strategies(info, bfu_state):
    strategies = []
    
    bounds = attempt_xml_dump(info['height'])
    if bounds:
        strategies.append(("Engine 1 (Dynamic XML Hierarchy)", calculate_grid_from_bounds(bounds)))
    else:
        print(f"{YELLOW}[*] Proceeding with Deep Math Engines...{RESET}")

    if info['brand'].lower() == 'samsung':
        strategies.append(("Engine 2 (Samsung Base Matrix)", calculate_samsung_grid(info, bfu_state)))
        strategies.append(("Engine 3 (Samsung State Crossover)", calculate_samsung_grid(info, not bfu_state)))
        strategies.append(("Engine 4 (Samsung Shifted High Matrix)", calculate_samsung_grid(info, bfu_state, shift_y=-0.02)))
        strategies.append(("Engine 5 (Samsung Shifted Low Matrix)", calculate_samsung_grid(info, bfu_state, shift_y=0.02)))
    else:
        # Aspect-based base ratio for AOSP
        aspect = info['height'] / info['width']
        base_y = 0.68 if aspect >= 2.1 else 0.66 if aspect >= 1.9 else 0.64
        
        strategies.append(("Engine 2 (Universal Base Matrix)", calculate_universal_grid(info, bfu_state, base_y)))
        strategies.append(("Engine 3 (Universal High Matrix)", calculate_universal_grid(info, bfu_state, base_y - 0.03)))
        strategies.append(("Engine 4 (Universal Low Matrix)", calculate_universal_grid(info, bfu_state, base_y + 0.04)))
        strategies.append(("Engine 5 (Universal Wide Matrix)", calculate_universal_grid(info, bfu_state, base_y, spread_x_ratio=0.31)))
        strategies.append(("Engine 6 (State Crossover Matrix)", calculate_universal_grid(info, not bfu_state, base_y)))
        
    return strategies

def get_line_points(p1, p2, steps=10):
    points = []
    for i in range(1, steps + 1):
        x = p1[0] + (p2[0] - p1[0]) * i / steps
        y = p1[1] + (p2[1] - p1[1]) * i / steps
        points.append((int(x), int(y)))
    return points

def prompt_user_pattern_interactive():
    root = tk.Tk()
    root.title("Android Smart Pattern Recovery")
    root.geometry("450x580")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    user_sequence = []
    selected_dots = []

    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    tk.Label(root, text="Draw Recovery Pattern", bg="#1e1e1e", fg="#00ffff", font=title_font).pack(pady=(25, 5))
    lbl_status = tk.Label(root, text="Click and drag your mouse to draw the pattern", bg="#1e1e1e", fg="#aaaaaa", font=("Helvetica", 11))
    lbl_status.pack(pady=(0, 15))

    canvas = tk.Canvas(root, width=350, height=350, bg="#1e1e1e", highlightthickness=0)
    canvas.pack()

    dots = {}
    r = 16
    pad = 75
    space = 100
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    idx = 0
    for row in range(3):
        for col in range(3):
            x = pad + col * space
            y = pad + row * space
            did = canvas.create_oval(x-r, y-r, x+r, y+r, fill="#444444", outline="#333333", width=2)
            dots[labels[idx]] = {'x': x, 'y': y, 'id': did}
            idx += 1

    lines = []

    def get_closest_dot(x, y):
        for lbl, d in dots.items():
            if math.hypot(d['x'] - x, d['y'] - y) < 30:
                return lbl
        return None

    def on_press(event):
        canvas.delete("temp_line")
        for l in lines: canvas.delete(l)
        lines.clear()
        user_sequence.clear()
        selected_dots.clear()
        for d in dots.values(): canvas.itemconfig(d['id'], fill="#444444")
        
        lbl = get_closest_dot(event.x, event.y)
        if lbl:
            user_sequence.append(lbl)
            selected_dots.append(dots[lbl])
            canvas.itemconfig(dots[lbl]['id'], fill="#00ff00")
            canvas.create_line(dots[lbl]['x'], dots[lbl]['y'], event.x, event.y, fill="#00ff00", width=5, tags="temp_line")
            lbl_status.config(text=f"Sequence: {''.join(user_sequence)}")

    def on_drag(event):
        if not user_sequence: return
        canvas.coords("temp_line", selected_dots[-1]['x'], selected_dots[-1]['y'], event.x, event.y)
        lbl = get_closest_dot(event.x, event.y)
        
        if lbl and lbl not in user_sequence:
            user_sequence.append(lbl)
            selected_dots.append(dots[lbl])
            canvas.itemconfig(dots[lbl]['id'], fill="#00ff00")
            if len(selected_dots) > 1:
                p1 = selected_dots[-2]
                p2 = selected_dots[-1]
                l = canvas.create_line(p1['x'], p1['y'], p2['x'], p2['y'], fill="#00ff00", width=5)
                lines.append(l)
            canvas.tag_raise("temp_line")
            lbl_status.config(text=f"Sequence: {''.join(user_sequence)}")

    def on_release(event):
        canvas.delete("temp_line")

    def clear_canvas():
        canvas.delete("temp_line")
        for l in lines: canvas.delete(l)
        lines.clear()
        user_sequence.clear()
        selected_dots.clear()
        for d in dots.values(): canvas.itemconfig(d['id'], fill="#444444")
        lbl_status.config(text="Click and drag your mouse to draw the pattern")

    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=20)

    def on_submit():
        if len(user_sequence) < 4:
            messagebox.showerror("Error", "Pattern must contain at least 4 dots.", parent=root)
            return
        root.destroy()

    def on_cancel():
        user_sequence.clear()
        root.destroy()

    tk.Button(btn_frame, text="Clear", bg="#555555", fg="white", font=("Helvetica", 11, "bold"), width=10, relief="flat", command=clear_canvas).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="Start Recovery", bg="#008cba", fg="white", font=("Helvetica", 11, "bold"), width=15, relief="flat", command=on_submit).grid(row=0, column=1, padx=8)
    tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white", font=("Helvetica", 11, "bold"), width=10, relief="flat", command=on_cancel).grid(row=0, column=2, padx=8)

    root.mainloop()
    return user_sequence

def execute_injection(points, sequence):
    script_content = "type= raw events\ncount= 1\nspeed= 1.0\nstart data >>\n"
    start_pt = points[sequence[0]]
    script_content += f"DispatchPointer(0, 0, 0, {start_pt[0]}, {start_pt[1]}, 1, 1, 0, 0, 0, 0, 0)\nUserWait(50)\n"

    for i in range(len(sequence) - 1):
        inter_points = get_line_points(points[sequence[i]], points[sequence[i+1]], steps=10)
        for pt in inter_points:
            script_content += f"DispatchPointer(0, 0, 2, {pt[0]}, {pt[1]}, 1, 1, 0, 0, 0, 0, 0)\nUserWait(20)\n"

    end_pt = points[sequence[-1]]
    script_content += f"DispatchPointer(0, 0, 1, {end_pt[0]}, {end_pt[1]}, 1, 1, 0, 0, 0, 0, 0)\n"

    with open("recovery_gesture.txt", "w", encoding='utf-8') as f:
        f.write(script_content)

    run_adb("adb push recovery_gesture.txt /data/local/tmp/recovery_gesture.txt")
    run_adb("adb shell monkey -f /data/local/tmp/recovery_gesture.txt 1")
    os.remove("recovery_gesture.txt")
    run_adb("adb shell rm -f /data/local/tmp/recovery_gesture.txt")

def verify_unlocked_state():
    time.sleep(2.5)
    
    power_dump = run_adb("adb shell dumpsys power")
    if "mHoldingDisplaySuspendBlocker=false" in power_dump or "Display Power: state=OFF" in power_dump:
        return False

    window_dump = run_adb("adb shell dumpsys window")
    keyguard_dump = run_adb("adb shell dumpsys keyguard")
    
    keyguard_indicators = [
        "mShowingLockscreen=true", 
        "showing=true", 
        "mKeyguardShowing=true",
        "mScreenOnFully=false"
    ]
    if any(indicator in window_dump or indicator in keyguard_dump for indicator in keyguard_indicators):
        return False
        
    current_focus = ""
    for line in window_dump.split('\n'):
        if "mCurrentFocus" in line:
            current_focus = line.strip().lower()
            break
            
    if "mcurrentfocus=null" in current_focus:
        if "iskeyguardlocked=true" in keyguard_dump or "mshowing=true" in keyguard_dump.lower():
            return False
            
    locked_keywords = ["keyguard", "lock", "bouncer", "notificationshade", "screenoff", "aod", "comboview"]
    for kw in locked_keywords:
        if kw in current_focus: 
            return False

    return True

def print_troubleshooting():
    print(f"\n{ORANGE}{BOLD}╭───────────────── Troubleshooting & Scientific Solutions ─────────────────╮{RESET}")
    print(f"{ORANGE}│ 1. All Engines Failed: Device DPI scaling is completely non-standard.  │{RESET}")
    print(f"{ORANGE}│ 2. Touch Latency: The device might be processing touches too slowly.   │{RESET}")
    print(f"{ORANGE}│    Solution: Increase 'UserWait(20)' to 'UserWait(40)' in the code.    │{RESET}")
    print(f"{ORANGE}│ 3. Incorrect Pattern: Double-check the drawn pattern sequence.         │{RESET}")
    print(f"{ORANGE}╰────────────────────────────────────────────────────────────────────────╯{RESET}")

def prompt_user_recovery_type():
    root = tk.Tk()
    root.title("Android Smart Recovery")
    root.geometry("400x320")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    choice = [None]

    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    btn_font = font.Font(family="Helvetica", size=12, weight="bold")

    tk.Label(root, text="Select Recovery Method", bg="#1e1e1e", fg="#00ffff", font=title_font).pack(pady=(20, 15))

    def select_pattern():
        choice[0] = "pattern"
        root.destroy()

    def select_pin():
        choice[0] = "pin"
        root.destroy()

    def select_password():
        choice[0] = "password"
        root.destroy()

    btn_pattern = tk.Button(root, text="Pattern Recovery", bg="#008cba", fg="white", font=btn_font, width=20, height=2, relief="flat", activebackground="#007ba0", activeforeground="white", command=select_pattern)
    btn_pattern.pack(pady=8)
    btn_pattern.bind("<Enter>", lambda e: btn_pattern.config(bg="#00a0d2"))
    btn_pattern.bind("<Leave>", lambda e: btn_pattern.config(bg="#008cba"))

    btn_pin = tk.Button(root, text="PIN Recovery", bg="#e0a800", fg="black", font=btn_font, width=20, height=2, relief="flat", activebackground="#c69500", activeforeground="black", command=select_pin)
    btn_pin.pack(pady=8)
    btn_pin.bind("<Enter>", lambda e: btn_pin.config(bg="#f3b807"))
    btn_pin.bind("<Leave>", lambda e: btn_pin.config(bg="#e0a800"))

    btn_password = tk.Button(root, text="Password Recovery", bg="#28a745", fg="white", font=btn_font, width=20, height=2, relief="flat", activebackground="#218838", activeforeground="white", command=select_password)
    btn_password.pack(pady=8)
    btn_password.bind("<Enter>", lambda e: btn_password.config(bg="#34ce57"))
    btn_password.bind("<Leave>", lambda e: btn_password.config(bg="#28a745"))

    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.mainloop()
    return choice[0]

def prompt_user_pin_interactive():
    root = tk.Tk()
    root.title("Android PIN Recovery")
    root.geometry("400x250")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    user_pin = [None]

    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    lbl_font = font.Font(family="Helvetica", size=11)
    btn_font = font.Font(family="Helvetica", size=11, weight="bold")

    tk.Label(root, text="Enter Device PIN", bg="#1e1e1e", fg="#00ffff", font=title_font).pack(pady=(25, 10))
    tk.Label(root, text="Enter the numeric PIN to test/verify:", bg="#1e1e1e", fg="#aaaaaa", font=lbl_font).pack(pady=(0, 15))

    entry_pin = tk.Entry(root, bg="#2a2a2a", fg="white", insertbackground="white", font=("Helvetica", 14), width=18, justify="center", show="")
    entry_pin.pack(pady=(0, 20))
    entry_pin.focus()

    # Show/Hide PIN toggle (Default to Show/True)
    show_pin = tk.BooleanVar(value=True)
    def toggle_pin_visibility():
        if show_pin.get():
            entry_pin.config(show="*")
            btn_toggle.config(text="Show PIN")
            show_pin.set(False)
        else:
            entry_pin.config(show="")
            btn_toggle.config(text="Hide PIN")
            show_pin.set(True)

    btn_toggle = tk.Button(root, text="Hide PIN", bg="#444444", fg="white", font=("Helvetica", 9), relief="flat", command=toggle_pin_visibility)
    btn_toggle.place(x=305, y=105, width=65, height=26)

    def on_submit():
        pin_val = entry_pin.get().strip()
        if not pin_val:
            messagebox.showerror("Error", "PIN cannot be empty.", parent=root)
            return
        if not pin_val.isdigit():
            messagebox.showerror("Error", "PIN must contain digits only.", parent=root)
            return
        user_pin[0] = pin_val
        root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=10)

    btn_submit = tk.Button(btn_frame, text="Start Recovery", bg="#008cba", fg="white", font=btn_font, width=15, relief="flat", command=on_submit)
    btn_submit.grid(row=0, column=0, padx=10)
    btn_submit.bind("<Enter>", lambda e: btn_submit.config(bg="#00a0d2"))
    btn_submit.bind("<Leave>", lambda e: btn_submit.config(bg="#008cba"))

    btn_cancel = tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white", font=btn_font, width=10, relief="flat", command=on_cancel)
    btn_cancel.grid(row=0, column=1, padx=10)
    btn_cancel.bind("<Enter>", lambda e: btn_cancel.config(bg="#ff5c4d"))
    btn_cancel.bind("<Leave>", lambda e: btn_cancel.config(bg="#f44336"))

    root.bind("<Return>", lambda event: on_submit())
    root.mainloop()
    return user_pin[0]

def prompt_user_password_interactive():
    root = tk.Tk()
    root.title("Android Password Recovery")
    root.geometry("400x250")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    user_password = [None]

    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    lbl_font = font.Font(family="Helvetica", size=11)
    btn_font = font.Font(family="Helvetica", size=11, weight="bold")

    tk.Label(root, text="Enter Device Password", bg="#1e1e1e", fg="#00ffff", font=title_font).pack(pady=(25, 10))
    tk.Label(root, text="Enter the password to test/verify:", bg="#1e1e1e", fg="#aaaaaa", font=lbl_font).pack(pady=(0, 15))

    entry_pw = tk.Entry(root, bg="#2a2a2a", fg="white", insertbackground="white", font=("Helvetica", 14), width=18, justify="center", show="")
    entry_pw.pack(pady=(0, 20))
    entry_pw.focus()

    # Show/Hide Password toggle (Default to Show/True)
    show_pw = tk.BooleanVar(value=True)
    def toggle_pw_visibility():
        if show_pw.get():
            entry_pw.config(show="*")
            btn_toggle.config(text="Show Password")
            show_pw.set(False)
        else:
            entry_pw.config(show="")
            btn_toggle.config(text="Hide Password")
            show_pw.set(True)

    btn_toggle = tk.Button(root, text="Hide Password", bg="#444444", fg="white", font=("Helvetica", 9), relief="flat", command=toggle_pw_visibility)
    btn_toggle.place(x=298, y=105, width=92, height=26)

    def on_submit():
        pw_val = entry_pw.get().strip()
        if not pw_val:
            messagebox.showerror("Error", "Password cannot be empty.", parent=root)
            return
        user_password[0] = pw_val
        root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=10)

    btn_submit = tk.Button(btn_frame, text="Start Recovery", bg="#008cba", fg="white", font=btn_font, width=15, relief="flat", command=on_submit)
    btn_submit.grid(row=0, column=0, padx=10)
    btn_submit.bind("<Enter>", lambda e: btn_submit.config(bg="#00a0d2"))
    btn_submit.bind("<Leave>", lambda e: btn_submit.config(bg="#008cba"))

    btn_cancel = tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white", font=btn_font, width=10, relief="flat", command=on_cancel)
    btn_cancel.grid(row=0, column=1, padx=10)
    btn_cancel.bind("<Enter>", lambda e: btn_cancel.config(bg="#ff5c4d"))
    btn_cancel.bind("<Leave>", lambda e: btn_cancel.config(bg="#f44336"))

    root.bind("<Return>", lambda event: on_submit())
    root.mainloop()
    return user_password[0]

def map_unicode_password_to_qwerty(password):
    arabic_map = {
        'ض': 'q', 'ص': 'w', 'ث': 'e', 'ق': 'r', 'ف': 't', 'غ': 'y', 'ع': 'u', 'ه': 'i', 'خ': 'o', 'ح': 'p', 'ج': '[', 'د': ']',
        'ش': 'a', 'س': 's', 'ي': 'd', 'ب': 'f', 'ل': 'g', 'ا': 'h', 'ت': 'j', 'ن': 'k', 'م': 'l', 'ك': ';', 'ط': "'",
        'ئ': 'z', 'ء': 'x', 'ؤ': 'c', 'ر': 'v', 'لا': 'b', 'ى': 'n', 'ة': 'm', 'و': ',', 'ز': '.', 'ظ': '/',
        'ذ': '`',
        'أ': 'H', 'إ': 'Y', 'آ': 'N', 'لأ': 'B', 'لإ': 'T', 'لآ': 'G',
        '؟': '?', '،': ',', '؛': ';',
        # Arabic-Indic digits to ASCII digits
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    mapped_chars = []
    i = 0
    while i < len(password):
        # Look ahead for two-character combinations like لأ, لإ, لآ
        if i + 1 < len(password) and password[i:i+2] in arabic_map:
            mapped_chars.append(arabic_map[password[i:i+2]])
            i += 2
        elif password[i] in arabic_map:
            mapped_chars.append(arabic_map[password[i]])
            i += 1
        else:
            mapped_chars.append(password[i])
            i += 1
            
    return "".join(mapped_chars)

def type_password_safe(pin):
    # Check if pin is purely alphanumeric (no spaces, no symbols)
    if pin.isalnum():
        # Type the entire string at once (very fast and safe)
        run_adb(["adb", "shell", "input", "text", pin])
    else:
        # Type character by character to handle spaces and symbols safely
        for char in pin:
            if char.isalnum():
                run_adb(["adb", "shell", "input", "text", char])
            elif char == " ":
                run_adb(["adb", "shell", "input", "text", "%s"])
            else:
                # Wrap symbols in double quotes to prevent Android shell syntax evaluation
                run_adb(["adb", "shell", "input", "text", f'"{char}"'])
            time.sleep(0.15)

def prompt_user_pin_action(is_unicode=False):
    root = tk.Tk()
    root.title("Action Choice")
    root.geometry("560x240" if is_unicode else "560x290")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    choice = [None]

    title_font = font.Font(family="Helvetica", size=15, weight="bold")
    desc_font = font.Font(family="Helvetica", size=10)
    btn_font = font.Font(family="Helvetica", size=11, weight="bold")
    warn_font = font.Font(family="Helvetica", size=9, weight="bold")

    tk.Label(root, text="Verified Successfully!", bg="#1e1e1e", fg="#00ff00", font=title_font).pack(pady=(20, 5))
    tk.Label(root, text="Select the action you want to perform on the device:", bg="#1e1e1e", fg="#aaaaaa", font=desc_font).pack(pady=(0, 15))

    if is_unicode:
        tk.Label(root, text="⚠️ 'Unlock Phone' (typing) is not supported for Unicode (Arabic/Chinese) passwords.\nPlease use 'Remove Password Completely' to unlock.", bg="#1e1e1e", fg="#ffcc00", font=warn_font).pack(pady=(0, 10))

    def select_unlock():
        choice[0] = "unlock"
        root.destroy()

    def select_clear():
        choice[0] = "clear"
        root.destroy()

    def select_none():
        choice[0] = "none"
        root.destroy()

    if not is_unicode:
        btn_unlock = tk.Button(root, text="Unlock Phone (Keep Password)", bg="#008cba", fg="white", font=btn_font, width=48, height=1, relief="flat", command=select_unlock)
        btn_unlock.pack(pady=6)
        btn_unlock.bind("<Enter>", lambda e: btn_unlock.config(bg="#00a0d2"))
        btn_unlock.bind("<Leave>", lambda e: btn_unlock.config(bg="#008cba"))

    btn_clear = tk.Button(root, text="Remove Password Completely (Clear Lock)", bg="#28a745", fg="white", font=btn_font, width=48, height=1, relief="flat", command=select_clear)
    btn_clear.pack(pady=6)
    btn_clear.bind("<Enter>", lambda e: btn_clear.config(bg="#218838"))
    btn_clear.bind("<Leave>", lambda e: btn_clear.config(bg="#28a745"))

    btn_none = tk.Button(root, text="No Action (Just report success)", bg="#555555", fg="white", font=btn_font, width=48, height=1, relief="flat", command=select_none)
    btn_none.pack(pady=6)
    btn_none.bind("<Enter>", lambda e: btn_none.config(bg="#6c757d"))
    btn_none.bind("<Leave>", lambda e: btn_none.config(bg="#555555"))

    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.mainloop()
    return choice[0]

def unlock_device_with_pin(pin, width, height):
    print(f"\n{CYAN}[+] Waking up device and preparing typing...{RESET}")
    # Wake screen safely using WAKEUP keyevent (does not toggle screen off if already awake)
    run_adb("adb shell input keyevent 224")
    time.sleep(0.5)
    # Dismiss keyguard / swipe up
    mid_x = width // 2
    run_adb(f"adb shell input swipe {mid_x} {int(height*0.9)} {mid_x} {int(height*0.1)} 250")
    time.sleep(2.5) # Wait 2.5 seconds to ensure lockscreen entry screen is fully ready
    
    # Type password safely (handles alphanumeric, spaces, and symbols correctly)
    type_password_safe(pin)
    time.sleep(0.5)
    # Press Enter
    run_adb("adb shell input keyevent 66")
    time.sleep(1.5)
    print(f"{GREEN}[+] Unlock keyevents sent to device.{RESET}")

def clear_lock_credential(pin):
    print(f"\n{CYAN}[+] Attempting to clear lock credential (removing password/PIN)...{RESET}")
    cmd = ["adb", "shell", "cmd", "lock_settings", "clear", "--old", pin]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    combined_output = (stdout + "\n" + stderr).strip()
    
    if "not found" in combined_output.lower() or "cmd: failure" in combined_output.lower():
        cmd = ["adb", "shell", "locksettings", "clear", "--old", pin]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        combined_output = (stdout + "\n" + stderr).strip()

    success = (result.returncode == 0) or ("successfully" in combined_output.lower()) or (not combined_output)
    if success:
        print(f"{GREEN}{BOLD}[+] SUCCESS: Lock credential cleared successfully! The phone is now unsecured (No PIN/Password).{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}[-] FAILURE: Could not clear lock credential.{RESET}")
        print(f"{YELLOW}[*] Device response:{RESET}\n{combined_output}")
        return False

def verify_pin_via_locksettings(pin):
    print(f"\n{CYAN}[+] Running verification...{RESET}")
    
    cmd = ["adb", "shell", "cmd", "lock_settings", "verify", "--old", pin]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    combined_output = (stdout + "\n" + stderr).strip()
    
    # Check if 'cmd' command was not found or failed due to cmd package issues
    if "not found" in combined_output.lower() or "cmd: failure" in combined_output.lower():
        # Fallback to legacy locksettings command
        cmd = ["adb", "shell", "locksettings", "verify", "--old", pin]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        combined_output = (stdout + "\n" + stderr).strip()

    success = (result.returncode == 0) or ("verified successfully" in combined_output.lower())
    return success, combined_output

def inject_pattern():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        
        devices = run_adb("adb devices").split('\n')
        if len([d for d in devices if d.strip()]) < 2 or 'device' not in devices[1]:
            print(f"{RED}[-] Device not detected or unauthorized. Please check USB debugging.{RESET}")
            choice = input(f"\n{YELLOW}Press Enter to retry, or type 'exit' to quit: {RESET}").strip().lower()
            if choice == 'exit':
                break
            continue

        recovery_type = prompt_user_recovery_type()
        if not recovery_type:
            print(f"{YELLOW}[!] Operation cancelled by user. Exiting...{RESET}")
            break

        if recovery_type == "pattern":
            sequence = prompt_user_pattern_interactive()
            if not sequence:
                print(f"{YELLOW}[!] Pattern drawing cancelled by user.{RESET}")
                input(f"\n{YELLOW}Press Enter to return to the main menu...{RESET}")
                continue
        elif recovery_type == "pin":
            pin = prompt_user_pin_interactive()
            if not pin:
                print(f"{YELLOW}[!] PIN entry cancelled by user.{RESET}")
                input(f"\n{YELLOW}Press Enter to return to the main menu...{RESET}")
                continue
        else:
            pin = prompt_user_password_interactive()
            if not pin:
                print(f"{YELLOW}[!] Password entry cancelled by user.{RESET}")
                input(f"\n{YELLOW}Press Enter to return to the main menu...{RESET}")
                continue

        # Screen Timeout Backup and Modify
        original_timeout = run_adb("adb shell settings get system screen_off_timeout")
        if original_timeout and original_timeout.isdigit():
            print(f"{CYAN}[+] Temporarily adjusting screen timeout to 60000ms (1 minute)...{RESET}")
            run_adb("adb shell settings put system screen_off_timeout 60000")

        info = get_device_info()
        bfu_state = is_before_first_unlock()
        
        print(f"{OCEAN_BLUE}[+] ━━━━━━━━━ Deep Device Telemetry ━━━━━━━━━{RESET}")
        print(f"    {YELLOW}Brand:{RESET}        {WHITE}{info['brand'].upper()} ({info['manufacturer']}){RESET}")
        print(f"    {YELLOW}Model:{RESET}        {WHITE}{info['model']}{RESET}")
        print(f"    {YELLOW}Board/SOC:{RESET}    {WHITE}{info['board']}{RESET}")
        print(f"    {YELLOW}Android:{RESET}      {WHITE}{info['android']} (API: {info['api_level']}){RESET}")
        print(f"    {YELLOW}Security:{RESET}     {WHITE}{info['security']}{RESET}")
        if info['oneui']: print(f"    {YELLOW}One UI:{RESET}       {LIGHT_BLUE}OneUI {info['oneui']}{RESET}")
        print(f"    {YELLOW}Resolution:{RESET}   {WHITE}{info['width']}x{info['height']} @ {info['dpi']} DPI{RESET}")
        print(f"    {YELLOW}USB Mode:{RESET}     {WHITE}{info['usb']}{RESET}")
        print(f"    {YELLOW}Crypto:{RESET}       {WHITE}{info['crypto_state']}{RESET}")
        print(f"    {YELLOW}FBE State:{RESET}    {WHITE}{'BFU (Just Rebooted)' if bfu_state else 'AFU (Normal Lock)'}{RESET}")
        print(f"{OCEAN_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

        if recovery_type == "pattern":
            ensure_screen_ready(info['width'], info['height'])
            strategies = build_attack_strategies(info, bfu_state)
            
            success = False
            for attempt, (engine_name, points) in enumerate(strategies, 1):
                print(f"\n{MAGENTA}[+] Executing Attempt {attempt}/{len(strategies)} using {engine_name}...{RESET}")
                
                if attempt > 1:
                    ensure_screen_ready(info['width'], info['height'], is_retry=True)
                    
                execute_injection(points, sequence)
                print(f"{CYAN}[+] Payload injected. Verifying lock screen status...{RESET}")
                
                if verify_unlocked_state():
                    print(f"\n{GREEN}{BOLD}[+] Verification Success: The device is UNLOCKED!{RESET}")
                    success = True
                    break
                else:
                    print(f"{YELLOW}[-] Verification Failed: The device is still locked. Moving to next engine...{RESET}")

            if not success:
                print_troubleshooting()
        else:
            # PIN / Password recovery flow via locksettings
            success, response = verify_pin_via_locksettings(pin)
            if success:
                print(f"\n{GREEN}{BOLD}[+] SUCCESS: Lock credential verified successfully!{RESET}")
                print(f"{GREEN}{BOLD}[+] Correct credential identified: {pin}{RESET}")
                
                is_unicode = not pin.isascii()
                
                # Prompt user for subsequent actions
                action = prompt_user_pin_action(is_unicode=is_unicode)
                if action == "unlock":
                    unlock_device_with_pin(pin, info['width'], info['height'])
                elif action == "clear":
                    clear_lock_credential(pin)
                else:
                    print(f"{YELLOW}[*] No post-verification action was executed.{RESET}")
            else:
                print(f"\n{RED}{BOLD}[-] FAILURE: Lock credential verification failed.{RESET}")
                print(f"{YELLOW}[*] Command Response:{RESET}\n{response}")

        # Restore Original Screen Timeout
        if original_timeout and original_timeout.isdigit():
            run_adb(f"adb shell settings put system screen_off_timeout {original_timeout}")
            print(f"\n{CYAN}[+] Restored original screen timeout to {original_timeout}ms{RESET}")

        print_footer()
        input(f"\n{YELLOW}Press Enter to return to the main menu...{RESET}")

if __name__ == "__main__":
    inject_pattern()