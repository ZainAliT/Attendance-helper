# 🎓 Attendance Helper

> **For students whose microphone fails during online classes — but are fully present and attending.**

When your mic breaks at attendance time, this tool listens for your name being called and automatically plays your pre-recorded voice ("Present") into Zoom, Google Meet, or Microsoft Teams — so you never get marked absent unfairly again.

![Platform Support](https://img.shields.io/badge/Platforms-Zoom%20%7C%20Google%20Meet%20%7C%20Teams-blue)
![Python](https://img.shields.io/badge/Python-3.11%20recommended-green)
![OS](https://img.shields.io/badge/OS-Windows%2010%2F11-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🖥️ **Multi-platform** — works with Zoom, Google Meet, Microsoft Teams, or any platform
- 🎙️ **Auto name detection** — listens to class audio and detects when your name is called
- ▶️ **Auto plays your voice** — instantly plays your recorded audio the moment your name is heard
- 🔊 **Virtual mic routing** — routes audio through VB-Cable into your platform as a real microphone
- ⌨️ **Hotkey support** — press F9 anytime to manually trigger playback as a backup
- 🧠 **Smart name matching** — detects first name, last name, or full name separately
- 💾 **Saves your settings** — remembers everything between sessions
- 🖥️ **Clean GUI** — no command line needed after setup

---

## 📋 Requirements

- **OS:** Windows 10 or Windows 11
- **Python:** 3.11 (strongly recommended — newer versions may have issues with pyaudio)
- **VB-Cable:** Free virtual audio driver — [vb-audio.com/Cable](https://vb-audio.com/Cable/)
- **Platform:** Zoom, Google Meet, Microsoft Teams, or any video call app

---

## 🚀 Setup Guide (Step by Step)

### Step 1 — Install Python 3.11

Download from 👉 [python.org/downloads/release/python-3119](https://www.python.org/downloads/release/python-3119/)

> ⚠️ **IMPORTANT:** On the first installer screen, check **"Add python.exe to PATH"** before clicking Install Now!

Verify it worked — open Command Prompt and run:
```bash
python --version
# Should show: Python 3.11.x
```

---

### Step 2 — Install VB-Cable (Virtual Microphone Driver)

VB-Cable creates a virtual audio pipe so your app's audio goes into Zoom/Meet/Teams as if it's your real mic.

1. Download from 👉 [vb-audio.com/Cable](https://vb-audio.com/Cable/)
2. Extract the ZIP file
3. Find `VBCABLE_Setup_x64.exe` → **Right-click → Run as administrator** ← very important!
4. Click **Install Driver**
5. **Restart your PC** ← the driver won't appear until you restart

---

### Step 3 — Download This Tool

**Option A — Git:**
```bash
git clone https://github.com/YOUR_USERNAME/attendance-helper.git
cd attendance-helper
```

**Option B — Direct download:**
Click the green **Code** button on GitHub → **Download ZIP** → extract it

---

### Step 4 — Create a Virtual Environment

Open Command Prompt or PowerShell in the project folder:

```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your command line. This means it's active.

> 💡 If `py -3.11` doesn't work, try `python -m venv venv`

---

### Step 5 — Install Dependencies

```bash
python -m pip install -r requirements.txt
```

> ⚠️ If `pyaudio` fails to install, make sure you're on Python 3.11. It doesn't support Python 3.12+ yet.
> 
> If it still fails, try: `python -m pip install pyaudio --find-links https://github.com/intxcc/pyaudio_portaudio/releases`

---

### Step 6 — Record Your "Present" Audio

Record yourself clearly saying **"Present"** (or "Here", "Yes sir", etc.) on your phone:

- **iPhone:** Use the **Voice Memos** app → saves as `.m4a`
- **Android:** Use the **Recorder** app → saves as `.mp3`

Then send the file to your PC via WhatsApp, email, or USB cable.

> ⚠️ The file must be audio only (`.mp3`, `.wav`, `.m4a`, `.ogg`). If you recorded a video, convert it at [cloudconvert.com/mp4-to-mp3](https://cloudconvert.com/mp4-to-mp3)

---

### Step 7 — Enable Stereo Mix (So App Can Hear Your Class)

This lets the app hear what's playing through your speakers — including your teacher's voice from Zoom/Meet.

1. Right-click the 🔊 speaker icon in your Windows taskbar
2. Click **Sounds**
3. Go to the **Recording** tab
4. Right-click on empty space → click **Show Disabled Devices**
5. You should see **Stereo Mix** appear → right-click it → **Enable**
6. Click OK

> 💡 If Stereo Mix doesn't appear, your sound card may not support it. In that case, use a physical cable to connect headphone output to mic input, or use a virtual audio loopback tool.

---

### Step 8 — Configure Your Platform's Microphone

You need to tell your video call app to use VB-Cable as the microphone:

**Zoom:**
1. Open Zoom → click the ⚙️ gear icon (top right)
2. Go to **Audio**
3. Under **Microphone** → select **"CABLE Output (VB-Audio Virtual Cable)"**

**Google Meet:**
1. In a meeting, click the ⋮ three-dot menu (bottom right)
2. Click **Settings**
3. Go to **Audio**
4. Under **Microphone** → select **"CABLE Output (VB-Audio Virtual Cable)"**

**Microsoft Teams:**
1. Click your profile picture → **Settings**
2. Go to **Devices**
3. Under **Microphone** → select **"CABLE Output (VB-Audio Virtual Cable)"**

---

### Step 9 — Run the App

```bash
python attendance_helper.py
```

---

## 🛠️ All Settings Explained

| Field | What it does | What to enter |
|---|---|---|
| **Platform** | Which app you're using for class | Click: Zoom / Google Meet / Teams / Other |
| **Your Name** | The name your teacher calls out | E.g. `Zain` or `Zain Tariq` — app detects first or last name |
| **Response Word** | What word you say for attendance | E.g. `Present`, `Here`, `Yes sir` |
| **Hotkey** | Key to manually play audio anytime | Default: `F9` — change to any key e.g. `F8`, `ctrl+p` |
| **Audio File** | Your recorded voice file | Click Browse → select your `.mp3` or `.wav` file |
| **Output Device** | Where audio gets sent (into the platform) | Select `CABLE Input (VB-Audio Virtual Cable)` |
| **Listen On** | Where the app listens for your name | Select `Stereo Mix` to hear your class audio |

---

## ▶️ How To Use (Every Class)

1. Open Command Prompt → `cd` to your project folder
2. Run `venv\Scripts\activate`
3. Run `python attendance_helper.py`
4. Select your **Platform** (Zoom / Meet / Teams)
5. Fill in your **Name**, **Audio File**, **Output Device**, **Listen On**
6. Click **💾 Save**
7. Click **▶ Start Listening**
8. Join your class as normal — the app runs in the background
9. When the teacher calls your name → audio plays automatically! ✅

---

## 🔁 Audio Flow Diagram

```
Teacher speaks in class
        ↓
Zoom/Meet/Teams plays audio through your speakers
        ↓
Stereo Mix captures that speaker audio
        ↓
App hears your name via Stereo Mix
        ↓
App plays your "Present" audio
        ↓
CABLE Input receives the audio
        ↓
CABLE Output sends it to Zoom/Meet/Teams as your mic
        ↓
Teacher hears "Present" ✅
```

---

## ❓ Troubleshooting

**`pyaudio` won't install:**
```bash
# Make sure you're on Python 3.11
py -3.11 -m venv venv
venv\Scripts\activate
python -m pip install pyaudio
```

**"CABLE Input/Output" not showing in dropdowns:**
- VB-Cable must be installed **as Administrator**
- You must **restart your PC** after installing VB-Cable

**App doesn't detect my name:**
- Make sure **Stereo Mix** is enabled (see Step 7)
- Make sure **"Listen On"** is set to Stereo Mix in the app
- Make sure your teacher's audio is actually playing through your speakers (not just headphones with no loopback)
- Try entering just your first name in the Name field

**Audio plays through my speakers instead of into the platform:**
- Set **Output Device** to `CABLE Input (VB-Audio Virtual Cable)`
- Set your platform's **Microphone** to `CABLE Output (VB-Audio Virtual Cable)`

**`pip` not recognized:**
Always use `python -m pip` instead of just `pip`:
```bash
python -m pip install -r requirements.txt
```

**App opens but nothing happens when I start listening:**
- Check the Activity Log in the app for error messages
- Make sure all libraries installed successfully
- Try clicking **🔊 Test Audio** first to confirm audio routing works

---

## 📁 Project Structure

```
attendance-helper/
├── attendance_helper.py   # Main application (run this)
├── requirements.txt       # Python library dependencies
├── README.md              # Full documentation (this file)
├── CONTRIBUTING.md        # How to contribute
├── .gitignore             # Files excluded from git
└── LICENSE                # MIT License
```

---

## 🤝 Contributing

Pull requests are welcome! If you find a bug or want a feature:

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test on Windows
4. Open a Pull Request with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for ideas and guidelines.

---

## ⚖️ Ethics & Intended Use

This tool is designed **only** for students who are **physically present and attending** their online class but face a technical issue (broken microphone) that prevents them from responding during attendance roll call.

It is **not** intended to fake attendance when you are absent. Please use it responsibly and honestly.

---

## 📄 License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

Built with ❤️ to solve a real student problem — never get marked absent because of a broken mic again.

---

*If this helped you, consider giving it a ⭐ on GitHub so other students can find it!*