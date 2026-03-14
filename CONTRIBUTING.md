# Contributing to Attendance Helper

Thanks for wanting to help! This tool was built to solve a real problem students face — mic failures during online class attendance. Every contribution helps more students.

---

## 🐛 Reporting Bugs

Open a GitHub Issue and include:

- Your **Windows version** (10 or 11)
- Your **Python version** (`python --version`)
- The **full error message** from the terminal or app log
- **Steps to reproduce** the problem
- Which **platform** you were using (Zoom / Meet / Teams)

---

## 💡 Suggesting Features

Open an Issue with the label `enhancement` and describe:
- What problem it solves
- How you'd expect it to work
- Any platform-specific behavior

---

## 🔧 Submitting Code

1. Fork the repository
2. Create a branch: `git checkout -b fix/your-fix-name`
3. Make your changes
4. Test it works on Windows with Python 3.11
5. Open a Pull Request with a clear description of what you changed and why

---

## 📋 Ideas & Roadmap

Here are features we'd love help with:

### Platform Support
- [ ] Better Google Meet integration (chat-based attendance detection)
- [ ] Microsoft Teams chat attendance support
- [ ] Webex / Cisco support
- [ ] BlackBoard Collaborate support

### Detection Improvements
- [ ] Fuzzy/phonetic name matching (handles mispronunciation)
- [ ] Offline speech recognition using Vosk (no internet needed)
- [ ] Confidence threshold setting in the UI
- [ ] Support for multiple name variations (nicknames)

### Audio
- [ ] Multiple response audio clips (randomly picks one to sound natural)
- [ ] Record audio directly inside the app (no phone needed)
- [ ] Audio preview waveform display
- [ ] Volume control for playback

### UI & UX
- [ ] System tray icon (minimize to tray)
- [ ] Auto-start with Windows option
- [ ] Dark/light theme toggle
- [ ] Multiple profiles (for students with multiple teachers)
- [ ] Notification sound when name is detected

### Platform
- [ ] macOS support
- [ ] Linux support
- [ ] Packaged `.exe` installer for Windows (no Python needed)

---

## 🧪 Testing Checklist

Before submitting a PR, please test:

- [ ] App launches without errors
- [ ] Settings save and reload correctly
- [ ] Platform selector buttons work and show correct tips
- [ ] Audio plays through VB-Cable correctly
- [ ] Name detection triggers audio playback
- [ ] Hotkey works
- [ ] Stop Listening button works cleanly

---

## 📝 Code Style

- Keep it readable — this project is meant to be student-friendly
- Add comments for anything non-obvious
- Avoid adding heavy dependencies unless necessary
- Test on Python 3.11 minimum