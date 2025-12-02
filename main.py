import time
import requests
import os
import sys
from threading import Thread
from pynput import mouse, keyboard
from tkinter import Tk, Label, Entry, Button
import winreg

API_URL = "https://ctrl.cloudplay.uz/api/inactive-pc/"
REG_PATH = r"SOFTWARE\NSDMonitor"

last_activity = time.time()
pc_number = None
interval = None   # yuborish oralig‘i (sekund)


# ---------------- Path helper ----------------

def get_exe_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(__file__)


# ---------------- Registry ----------------

def save_settings(pc_number, interval):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    winreg.SetValueEx(key, "pc_number", 0, winreg.REG_SZ, pc_number)
    winreg.SetValueEx(key, "interval", 0, winreg.REG_SZ, str(interval))
    key.Close()


def load_pc_number():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, "pc_number")
        return value
    except:
        return None


def load_interval():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, "interval")
        return int(value)
    except:
        return None


def add_to_startup():
    exe_path = get_exe_path()
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "NSDMonitorApp", 0, winreg.REG_SZ, exe_path)
    key.Close()


# ---------------- GUI ----------------

def ask_settings_gui():
    def save_and_close():
        pc = entry_pc.get().strip()
        intr = entry_interval.get().strip()

        if pc and intr.isdigit():
            save_settings(pc, int(intr))
            window.destroy()

    window = Tk()
    window.title("Kompyuter sozlamalari")
    window.geometry("300x180")

    Label(window, text="Kompyuter raqami:").pack(pady=5)
    entry_pc = Entry(window, width=25)
    entry_pc.pack(pady=5)

    Label(window, text="Necha sekundda yuborilsin?").pack(pady=5)
    entry_interval = Entry(window, width=25)
    entry_interval.insert(0, "300")  # default: 120 sekund
    entry_interval.pack(pady=5)

    Button(window, text="Saqlash", command=save_and_close).pack(pady=10)

    window.mainloop()


# ---------------- Activity monitor ----------------

def on_activity(x=None, y=None):
    global last_activity
    last_activity = time.time()


def start_listeners():
    mouse.Listener(on_move=on_activity, on_click=on_activity).start()
    keyboard.Listener(on_press=on_activity).start()


def send_idle(pc):
    try:
        requests.post(API_URL, json={"comp_number": pc}, timeout=5)
    except:
        pass


def monitor():
    global last_activity, interval

    while True:
        if time.time() - last_activity >= interval:
            send_idle(pc_number)
            last_activity = time.time()

        time.sleep(2)


# ---------------- Main ----------------

pc_number = load_pc_number()
interval = load_interval()

# Agar sozlamalar yo‘q bo‘lsa GUI ochiladi
if not pc_number or not interval:
    ask_settings_gui()
    pc_number = load_pc_number()
    interval = load_interval()

add_to_startup()
start_listeners()

t = Thread(target=monitor)
t.daemon = True
t.start()

while True:
    time.sleep(1)
