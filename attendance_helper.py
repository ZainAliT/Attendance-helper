"""
🎓 Attendance Helper - For when your mic fails but you're fully present!
Supports: Zoom, Google Meet, Microsoft Teams

Listens for your name and auto-plays your "Present" audio into any platform.

Requirements (install once):
  python -m pip install sounddevice soundfile numpy speechrecognition pyaudio keyboard

Also install VB-Cable from https://vb-audio.com/Cable/ (free virtual mic driver)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
import json
import time
import webbrowser

# ── optional imports (graceful fallback if not installed yet) ──────────────────
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import keyboard
    HAS_KB = True
except ImportError:
    HAS_KB = False

# ── Config ─────────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".attendance_helper.json")

PLATFORMS = {
    "Zoom": {
        "icon": "🔵",
        "color": "#2D8CFF",
        "tip": "In Zoom: Settings ⚙️ → Audio → Microphone → select 'CABLE Output (VB-Audio Virtual Cable)'",
    },
    "Google Meet": {
        "icon": "🟢",
        "color": "#34A853",
        "tip": "In Meet: click ⋮ (3 dots) → Settings → Audio → Microphone → select 'CABLE Output (VB-Audio Virtual Cable)'",
    },
    "Microsoft Teams": {
        "icon": "🟣",
        "color": "#6264A7",
        "tip": "In Teams: click ⋯ → Settings → Devices → Microphone → select 'CABLE Output (VB-Audio Virtual Cable)'",
    },
    "Other": {
        "icon": "⚪",
        "color": "#8B949E",
        "tip": "In your platform's audio settings, set Microphone to 'CABLE Output (VB-Audio Virtual Cable)'",
    },
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "name": "", "audio_path": "", "output_device": "",
        "input_device": "", "hotkey": "F9", "platform": "Zoom",
        "response_word": "Present"
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

# ── Main App ───────────────────────────────────────────────────────────────────
class AttendanceHelper(tk.Tk):
    BG      = "#0D1117"
    CARD    = "#161B22"
    BORDER  = "#30363D"
    TEXT    = "#E6EDF3"
    MUTED   = "#8B949E"
    SUCCESS = "#3FB950"
    WARNING = "#D29922"
    DANGER  = "#F85149"
    ACCENT  = "#4FC3F7"

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.listening = False
        self.log_queue = queue.Queue()
        self._listen_thread = None
        self._platform_color = self.ACCENT

        self.title("🎓 Attendance Helper")
        self.geometry("640x780")
        self.minsize(560, 660)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        self._build_ui()
        self._check_deps()
        self._poll_log()

        if HAS_KB and self.cfg.get("hotkey"):
            self._bind_hotkey(self.cfg["hotkey"])

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=self.BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🎓", font=("Segoe UI Emoji", 28), bg=self.BG).pack(side="left")
        tf = tk.Frame(hdr, bg=self.BG)
        tf.pack(side="left", padx=12)
        tk.Label(tf, text="Attendance Helper", font=("Segoe UI", 18, "bold"),
                 fg=self.TEXT, bg=self.BG).pack(anchor="w")
        tk.Label(tf, text="Auto-plays your voice when mic fails  •  Zoom  •  Meet  •  Teams",
                 font=("Segoe UI", 9), fg=self.MUTED, bg=self.BG).pack(anchor="w")

        self.status_var = tk.StringVar(value="● Idle")
        self.status_lbl = tk.Label(hdr, textvariable=self.status_var,
                                   font=("Segoe UI", 9, "bold"),
                                   fg=self.MUTED, bg=self.BORDER,
                                   padx=10, pady=4, relief="flat")
        self.status_lbl.pack(side="right")

        self._divider()
        self._card_section("🖥️  Platform", self._build_platform)
        self._divider()
        self._card_section("⚙️  Setup", self._build_setup)
        self._divider()

        # Controls
        ctrl = tk.Frame(self, bg=self.BG)
        ctrl.pack(fill="x", padx=24, pady=12)

        self.listen_btn = tk.Button(ctrl, text="▶  Start Listening",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=self.SUCCESS, fg=self.BG,
                                    relief="flat", padx=18, pady=10,
                                    cursor="hand2", command=self.toggle_listen)
        self.listen_btn.pack(side="left")

        tk.Button(ctrl, text="🔊  Test Audio",
                  font=("Segoe UI", 11), bg=self.CARD, fg=self.TEXT,
                  relief="flat", padx=18, pady=10,
                  cursor="hand2", command=self.play_audio).pack(side="left", padx=10)

        tk.Button(ctrl, text="💾  Save",
                  font=("Segoe UI", 11), bg=self.CARD, fg=self.TEXT,
                  relief="flat", padx=18, pady=10,
                  cursor="hand2", command=self.save_settings).pack(side="right")

        self._divider()

        # Log
        tk.Label(self, text="Activity Log", font=("Segoe UI", 9, "bold"),
                 fg=self.MUTED, bg=self.BG).pack(anchor="w", padx=24)
        log_frame = tk.Frame(self, bg=self.CARD, bd=0,
                             highlightbackground=self.BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(6, 20))
        self.log_box = tk.Text(log_frame, bg=self.CARD, fg=self.MUTED,
                               font=("Cascadia Code", 9), relief="flat",
                               state="disabled", wrap="word",
                               padx=10, pady=10, insertbackground=self.TEXT)
        scroll = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_box.pack(fill="both", expand=True)
        self._log("Welcome! Choose your platform, fill settings, then Start.", "info")

    def _build_platform(self, parent):
        self.platform_var = tk.StringVar(value=self.cfg.get("platform", "Zoom"))
        btn_frame = tk.Frame(parent, bg=self.CARD)
        btn_frame.pack(fill="x", pady=(0, 8))

        self.platform_btns = {}
        for name, info in PLATFORMS.items():
            btn = tk.Button(btn_frame,
                            text=f"{info['icon']}  {name}",
                            font=("Segoe UI", 10, "bold"),
                            relief="flat", padx=14, pady=8,
                            cursor="hand2",
                            command=lambda n=name: self._select_platform(n))
            btn.pack(side="left", padx=(0, 6))
            self.platform_btns[name] = btn

        self.platform_tip = tk.Label(parent, text="",
                                     font=("Segoe UI", 8), fg=self.ACCENT,
                                     bg=self.CARD, wraplength=540, justify="left")
        self.platform_tip.pack(anchor="w", pady=(4, 0))
        self._select_platform(self.cfg.get("platform", "Zoom"), save=False)

    def _select_platform(self, name, save=True):
        self.platform_var.set(name)
        info = PLATFORMS[name]
        self._platform_color = info["color"]
        for n, btn in self.platform_btns.items():
            btn.configure(bg=info["color"] if n == name else self.BORDER,
                          fg="white" if n == name else self.MUTED)
        self.platform_tip.configure(text=f"💡 {info['tip']}")
        if save:
            self.cfg["platform"] = name

    def _build_setup(self, parent):
        self._field_row(parent, "Your Name (as teacher calls you):",
                        "name_entry", self.cfg.get("name", ""))
        self._field_row(parent, "Response word (Present / Here / Yes):",
                        "response_entry", self.cfg.get("response_word", "Present"))
        self._field_row(parent, "Hotkey to manually trigger (e.g. F9):",
                        "hotkey_entry", self.cfg.get("hotkey", "F9"))

        # Audio file picker
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Audio file (your recorded voice):",
                 font=("Segoe UI", 9), fg=self.MUTED, bg=self.CARD,
                 width=34, anchor="w").pack(side="left")
        self.audio_path_var = tk.StringVar(value=self.cfg.get("audio_path", ""))
        tk.Entry(row, textvariable=self.audio_path_var,
                 bg="#0D1117", fg=self.TEXT, relief="flat",
                 font=("Segoe UI", 9), insertbackground=self.TEXT,
                 highlightbackground=self.BORDER, highlightthickness=1).pack(
                 side="left", fill="x", expand=True, ipady=5)
        tk.Button(row, text="Browse", bg=self.BORDER, fg=self.TEXT,
                  font=("Segoe UI", 9), relief="flat", padx=8,
                  cursor="hand2", command=self._browse_audio).pack(side="left", padx=(6, 0))

        # Output device
        row2 = tk.Frame(parent, bg=self.CARD)
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Output device (VB-Cable → platform mic):",
                 font=("Segoe UI", 9), fg=self.MUTED, bg=self.CARD,
                 width=34, anchor="w").pack(side="left")
        out_devs = self._get_output_devices()
        saved_out = self.cfg.get("output_device", "")
        default_out = saved_out if saved_out in out_devs else (out_devs[0] if out_devs else "")
        self.device_var = tk.StringVar(value=default_out)
        ttk.Combobox(row2, textvariable=self.device_var, values=out_devs,
                     state="readonly", font=("Segoe UI", 9)).pack(
                     side="left", fill="x", expand=True, ipady=3)

        # Input device
        row3 = tk.Frame(parent, bg=self.CARD)
        row3.pack(fill="x", pady=4)
        tk.Label(row3, text="Listen on (Stereo Mix to hear class audio):",
                 font=("Segoe UI", 9), fg=self.MUTED, bg=self.CARD,
                 width=34, anchor="w").pack(side="left")
        in_devs = self._get_input_devices()
        saved_in = self.cfg.get("input_device", "")
        default_in = saved_in if saved_in in in_devs else (in_devs[0] if in_devs else "")
        self.input_device_var = tk.StringVar(value=default_in)
        ttk.Combobox(row3, textvariable=self.input_device_var, values=in_devs,
                     state="readonly", font=("Segoe UI", 9)).pack(
                     side="left", fill="x", expand=True, ipady=3)

        tk.Label(parent,
                 text="⚠️  Stereo Mix not visible? Right-click taskbar speaker → Sounds → Recording tab → right-click empty area → Show Disabled Devices → Enable Stereo Mix",
                 font=("Segoe UI", 8), fg=self.WARNING,
                 bg=self.CARD, wraplength=520, justify="left").pack(anchor="w", pady=(6, 0))

    # ── DEVICES ────────────────────────────────────────────────────────────────
    def _get_output_devices(self):
        if not HAS_AUDIO:
            return ["(install sounddevice first)"]
        try:
            devs = sd.query_devices()
            out = [d["name"] for d in devs if d["max_output_channels"] > 0]
            out.sort(key=lambda x: 0 if "cable" in x.lower() or "vb" in x.lower() else 1)
            return out or ["Default"]
        except Exception:
            return ["Default"]

    def _get_input_devices(self):
        if not HAS_SR:
            return ["(install SpeechRecognition first)"]
        try:
            names = sr.Microphone.list_microphone_names()
            names.sort(key=lambda x: 0 if any(k in x.lower() for k in
                       ["stereo mix", "wave out", "speaker", "loopback", "what u hear"]) else 1)
            return names if names else ["Default"]
        except Exception:
            return ["Default"]

    def _browse_audio(self):
        path = filedialog.askopenfilename(
            title="Select your recorded audio file",
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg *.flac *.m4a"), ("All files", "*.*")])
        if path:
            self.audio_path_var.set(path)

    # ── SETTINGS ───────────────────────────────────────────────────────────────
    def save_settings(self):
        self.cfg["name"]          = self.name_entry_var.get().strip()
        self.cfg["response_word"] = self.response_entry_var.get().strip() or "Present"
        self.cfg["hotkey"]        = self.hotkey_entry_var.get().strip() or "F9"
        self.cfg["audio_path"]    = self.audio_path_var.get().strip()
        self.cfg["output_device"] = self.device_var.get()
        self.cfg["input_device"]  = self.input_device_var.get()
        self.cfg["platform"]      = self.platform_var.get()
        save_config(self.cfg)
        if HAS_KB:
            self._bind_hotkey(self.cfg["hotkey"])
        self._log(f"✅ Saved! Platform: {self.cfg['platform']} | Name: {self.cfg['name']} | Hotkey: {self.cfg['hotkey']}", "success")

    def _bind_hotkey(self, key):
        try:
            keyboard.unhook_all_hotkeys()
            keyboard.add_hotkey(key, self.play_audio)
            self._log(f"Hotkey '{key}' bound — press anytime to play audio.", "info")
        except Exception as e:
            self._log(f"Hotkey error: {e}", "warn")

    # ── LISTEN TOGGLE ──────────────────────────────────────────────────────────
    def toggle_listen(self):
        if self.listening:
            self.listening = False
            self.listen_btn.configure(text="▶  Start Listening", bg=self.SUCCESS)
            self._set_status("● Idle", self.MUTED)
            self._log("Stopped listening.", "info")
        else:
            name = self.name_entry_var.get().strip()
            if not name:
                messagebox.showwarning("Name required", "Please enter your name first.")
                return
            if not HAS_SR:
                messagebox.showerror("Missing library",
                    "SpeechRecognition not installed.\nRun: python -m pip install SpeechRecognition pyaudio")
                return
            platform = self.platform_var.get()
            self.listening = True
            self.listen_btn.configure(text="⏹  Stop Listening", bg=self.DANGER)
            self._set_status(f"● Listening on {platform}…", self._platform_color)
            self._log(f"▶ Listening for '{name}' on {platform}…", "success")
            self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._listen_thread.start()

    # ── SPEECH RECOGNITION LOOP ────────────────────────────────────────────────
    def _listen_loop(self):
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        name = self.cfg.get("name", "").lower()

        device_index = None
        selected = self.cfg.get("input_device", "")
        if selected and selected != "Default":
            try:
                all_mics = sr.Microphone.list_microphone_names()
                if selected in all_mics:
                    device_index = all_mics.index(selected)
            except Exception:
                pass

        try:
            mic = sr.Microphone(device_index=device_index)
        except Exception as e:
            self.log_queue.put((f"Mic error: {e} — using default", "warn"))
            mic = sr.Microphone()

        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            self.log_queue.put((f"🎙️ Calibrated. Listening on: {selected or 'Default mic'}", "info"))

            while self.listening:
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=8)
                    text = r.recognize_google(audio).lower()
                    self.log_queue.put((f"Heard: \"{text}\"", "muted"))

                    # Match any part of the name (handles first name, last name, full name)
                    name_parts = [p for p in name.split() if len(p) > 2]
                    if any(part in text for part in name_parts):
                        self.log_queue.put((f"🔔 NAME DETECTED: \"{text}\" — auto-playing!", "warn"))
                        self.after(0, self.play_audio)

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.log_queue.put((f"Speech API error: {e}", "error"))
                    time.sleep(3)
                except Exception as e:
                    self.log_queue.put((f"Error: {e}", "error"))
                    time.sleep(1)

    # ── PLAY AUDIO ─────────────────────────────────────────────────────────────
    def play_audio(self):
        path = self.audio_path_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showwarning("No audio file", "Please select your recorded audio file first.")
            return
        if not HAS_AUDIO:
            messagebox.showerror("Missing library",
                "sounddevice not installed.\nRun: python -m pip install sounddevice soundfile")
            return

        def _play():
            try:
                device_name = self.device_var.get()
                device_idx = None
                if device_name and device_name != "Default":
                    devs = sd.query_devices()
                    for i, d in enumerate(devs):
                        if d["name"] == device_name and d["max_output_channels"] > 0:
                            device_idx = i
                            break
                data, fs = sf.read(path, dtype="float32")
                sd.play(data, fs, device=device_idx)
                sd.wait()
                platform = self.cfg.get("platform", "platform")
                self.log_queue.put((f"✅ Audio played into {platform}!", "success"))
            except Exception as e:
                self.log_queue.put((f"Playback error: {e}", "error"))

        threading.Thread(target=_play, daemon=True).start()
        self._log(f"▶ Playing into {self.cfg.get('platform', 'platform')}…", "info")

    # ── HELPERS ────────────────────────────────────────────────────────────────
    def _card_section(self, title, builder):
        tk.Label(self, text=title, font=("Segoe UI", 10, "bold"),
                 fg=self.TEXT, bg=self.BG).pack(anchor="w", padx=24, pady=(12, 4))
        card = tk.Frame(self, bg=self.CARD, bd=0,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="x", padx=24)
        inner = tk.Frame(card, bg=self.CARD, padx=16, pady=12)
        inner.pack(fill="x")
        builder(inner)

    def _field_row(self, parent, label, attr, default):
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, font=("Segoe UI", 9), fg=self.MUTED,
                 bg=self.CARD, width=34, anchor="w").pack(side="left")
        var = tk.StringVar(value=default)
        setattr(self, attr + "_var", var)
        entry = tk.Entry(row, textvariable=var, bg="#0D1117", fg=self.TEXT,
                         relief="flat", font=("Segoe UI", 9), insertbackground=self.TEXT,
                         highlightbackground=self.BORDER, highlightthickness=1)
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        setattr(self, attr, entry)

    def _divider(self):
        tk.Frame(self, bg=self.BORDER, height=1).pack(fill="x", padx=24, pady=8)

    def _set_status(self, text, color):
        self.status_var.set(text)
        self.status_lbl.configure(fg=color)

    def _log(self, msg, kind="info"):
        colors = {"info": self.MUTED, "success": self.SUCCESS,
                  "warn": self.WARNING, "error": self.DANGER, "muted": "#444"}
        self.log_box.configure(state="normal")
        ts = time.strftime("%H:%M:%S")
        tag = f"{kind}_{ts}_{id(msg)}"
        self.log_box.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_box.tag_configure(tag, foreground=colors.get(kind, self.MUTED))
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _poll_log(self):
        try:
            while True:
                msg, kind = self.log_queue.get_nowait()
                self._log(msg, kind)
        except queue.Empty:
            pass
        self.after(200, self._poll_log)

    def _check_deps(self):
        missing = []
        if not HAS_AUDIO:
            missing.append("sounddevice soundfile numpy")
        if not HAS_SR:
            missing.append("SpeechRecognition pyaudio")
        if not HAS_KB:
            missing.append("keyboard")
        if missing:
            self._log("⚠️  Missing libraries! Run: python -m pip install " + " ".join(missing), "warn")
        else:
            self._log("✅ All libraries found. Ready to go!", "success")

# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AttendanceHelper()
    app.mainloop()