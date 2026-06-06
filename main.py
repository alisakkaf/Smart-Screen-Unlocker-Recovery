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
    print(f"{YELLOW}{BOLD}                 Android Smart Pattern Recovery v1.0                  {RESET}")
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
    print(f"{CYAN}[+] Verifying lock screen status...{RESET}")
    
    window_dump = run_adb("adb shell dumpsys window")
    keyguard_dump = run_adb("adb shell dumpsys keyguard")
    
    if "mShowingLockscreen=true" in window_dump or "showing=true" in keyguard_dump:
        return False
        
    current_focus = ""
    for line in window_dump.split('\n'):
        if "mCurrentFocus" in line:
            current_focus = line.strip().lower()
            break
            
    locked_keywords = ["keyguard", "lock", "bouncer", "notificationshade", "screenoff", "aod"]
    for kw in locked_keywords:
        if kw in current_focus:
            return False
            
    return True

def inject_pattern():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    devices = run_adb("adb devices").split('\n')
    if len([d for d in devices if d.strip()]) < 2 or 'device' not in devices[1]:
        print(f"{RED}[-] Device not detected or unauthorized. Please check USB debugging.{RESET}")
        return

    sequence = prompt_user_pattern_interactive()
    if not sequence:
        print(f"{YELLOW}[!] Operation cancelled by user.{RESET}")
        return

    print(f"{CYAN}[+] Temporarily adjusting screen timeout to 300000ms (5 minutes)...{RESET}")
    run_adb("adb shell settings put system screen_off_timeout 300000")

    info = get_device_info()
    bfu_state = is_before_first_unlock()
    
    print(f"\n{OCEAN_BLUE}[+] ━━━━━━━━━ Deep Device Telemetry ━━━━━━━━━{RESET}")
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

    ensure_screen_ready(info['width'], info['height'])
    strategies = build_attack_strategies(info, bfu_state)
    
    success = False
    for attempt, (engine_name, points) in enumerate(strategies, 1):
        print(f"\n{MAGENTA}[+] Executing Attempt {attempt}/{len(strategies)} using {engine_name}...{RESET}")
        start_pt = points['A']
        print(f"{WHITE}    [*] Grid Start Point (A): X={start_pt[0]}, Y={start_pt[1]}{RESET}")
        
        if attempt > 1:
            ensure_screen_ready(info['width'], info['height'], is_retry=True)
            
        print(f"{CYAN}[+] Generating Smart Action script for sequence: {''.join(sequence)}...{RESET}")
        execute_injection(points, sequence)
        print(f"{CYAN}[+] Executing fluid pattern operation via kernel...{RESET}")
        
        if verify_unlocked_state():
            print(f"\n{GREEN}{BOLD}[+] Task Completed Successfully! The device is UNLOCKED!{RESET}")
            success = True
            break
        else:
            print(f"{YELLOW}[-] Verification Failed: The device is still locked. Moving to next engine...{RESET}")

    if not success:
        print(f"\n{RED}{BOLD}[-] All Engines Failed: The device appears to be STILL LOCKED.{RESET}")

    print_footer()

if __name__ == "__main__":
    inject_pattern()