# 🌱 Luna — AI-Powered Autonomous Plant Care System
### Your Complete Beginner's Project Guide

> **Teaching Philosophy**: You will *build* this yourself. I'll guide every step, explain every concept, and celebrate every win. Let's grow together — just like Luna! 🌿

---

## 🗺️ Project Roadmap (All Phases at a Glance)

| Phase | Name | What You Build |
|-------|------|----------------|
| 1 | 🛠️ Setup & Workspace | Tools, folders, API keys |
| 2 | 🔌 Arduino Sensors | Read real sensor data |
| 3 | 🐍 Python Bridge | Connect Arduino ↔ Python |
| 4 | 🧠 AI Brain | Gemini API integration |
| 5 | 💬 Luna's Voice | Speech-to-text + Text-to-speech |
| 6 | 📊 Memory & Data | Store history, spot trends |
| 7 | 🩺 Health Scoring | AI health predictions |
| 8 | 📅 Daily Care Plans | AI-generated schedules |
| 9 | 🔄 Self-Healing | Handle failures gracefully |
| 10 | 🎨 Dashboard | Visual interface for Luna |

---

## ✅ Phase 1 — Setup Your Workspace

> **Stop after this phase and tell me "Phase 1 done" when finished!**

---

### 🎯 Goal

Set up your computer so it's ready to run all parts of this project:
Python, Arduino IDE, voice tools (Vosk + Piper), and your AI cloud API.

---

### 🤔 Why Is This Phase Important?

Think of this like building a house. Before laying bricks, you need:
- The right **tools** (hammer, nails) → Python, Arduino IDE
- A **blueprint** (folder structure) → your project directories
- **Permits and keys** (credentials) → your Gemini API key

If your foundation is messy, everything built on top of it breaks. One clean setup now saves you hours of frustration later.

---

### 🪜 Step-by-Step Instructions

#### Step 1 — Install Python (3.10 or 3.11 recommended)

1. Go to 👉 https://www.python.org/downloads/
2. Download Python **3.11.x** (the `.exe` installer for Windows)
3. Run the installer
4. ⚠️ **CRITICAL**: On the first screen, check the box that says **"Add Python to PATH"** before clicking Install

**How to verify it worked:**
Open your terminal (search "cmd" or "PowerShell" in Windows) and type:
```
python --version
```
You should see something like: `Python 3.11.9`

---

#### Step 2 — Install Arduino IDE

1. Go to 👉 https://www.arduino.cc/en/software
2. Download **Arduino IDE 2.x** for Windows
3. Install it normally (Next → Next → Install)
4. Open it once just to confirm it launches

You don't need to plug in your Arduino yet. Just confirm the IDE opens.

---

#### Step 3 — Install VS Code (Your Code Editor)

If you don't already have it:
1. Go to 👉 https://code.visualstudio.com/
2. Download and install it
3. Open VS Code, then install the **Python extension** (search in Extensions tab)

> 💡 You'll write all your Python code here. Arduino code goes in the Arduino IDE.

---

#### Step 4 — Create Your Project Folder Structure

Open your terminal and navigate to your project location:
```
C:\Users\HP\Documents\AI Plant Monitor\
```

Now create this folder structure **manually** (you can use File Explorer or the terminal):

```
AI Plant Monitor/
│
├── arduino/
│   └── luna_sensors/
│       └── luna_sensors.ino        ← Arduino sketch (Phase 2)
│
├── python/
│   ├── main.py                     ← Entry point (Phase 3)
│   ├── config.py                   ← API keys & settings
│   ├── serial_reader.py            ← Reads from Arduino (Phase 3)
│   ├── ai_brain.py                 ← Gemini AI logic (Phase 4)
│   ├── voice_agent.py              ← Vosk + Piper (Phase 5)
│   ├── memory.py                   ← Data storage (Phase 6)
│   ├── health_scorer.py            ← Health analysis (Phase 7)
│   ├── scheduler.py                ← Daily care plans (Phase 8)
│   └── self_healer.py              ← Error recovery (Phase 9)
│
├── data/
│   ├── sensor_logs/                ← Raw sensor readings (CSV files)
│   └── luna_memory.json            ← Luna's "brain memory"
│
├── voice/
│   ├── vosk_model/                 ← Vosk speech model goes here
│   └── piper_voices/               ← Piper TTS voice files go here
│
├── dashboard/
│   └── index.html                  ← Simple web dashboard (Phase 10)
│
├── .env                            ← 🔐 Your secret API key (NEVER share this!)
├── requirements.txt                ← List of Python packages
└── README.md                       ← Project notes (this file!)
```

> 🎉 Create all of these folders and empty files now. Even blank files are fine for now. We'll fill them in phase by phase!

---

#### Step 5 — Set Up a Python Virtual Environment

A **virtual environment** keeps your project's packages separate from the rest of your computer. Think of it as Luna's personal toolbox.

In your terminal, navigate to your project folder:
```
cd "C:\Users\HP\Documents\AI Plant Monitor"
```

Then create and activate the virtual environment:
```
python -m venv luna_env
luna_env\Scripts\activate
```

✅ You'll know it worked when you see `(luna_env)` at the start of your terminal prompt.

> ⚠️ You must activate this environment **every time** you work on the project!

---

#### Step 6 — Install Python Libraries

With your virtual environment active, install the required packages one by one. This is good practice — you understand what each one does:

```
pip install pyserial          # Reads data from Arduino via USB
pip install google-generativeai  # Google Gemini AI API
pip install python-dotenv     # Reads your .env secret key file
pip install vosk              # Speech-to-text (listens to you)
pip install schedule          # Runs tasks on a timer
pip install pandas            # Handles sensor data in tables
pip install requests          # Makes HTTP calls to APIs
```

After installing, create your `requirements.txt` by running:
```
pip freeze > requirements.txt
```

> 💡 `requirements.txt` is like a shopping list. Anyone can recreate your environment with it later using `pip install -r requirements.txt`.

---

#### Step 7 — Install Vosk Speech Model

Vosk needs a **language model** to understand speech. We use a small offline model.

1. Go to 👉 https://alphacephei.com/vosk/models
2. Download: **`vosk-model-small-en-us-0.15`** (it's only ~40 MB)
3. Unzip the downloaded file
4. Place the unzipped folder **inside** your `voice/vosk_model/` directory

Your folder should look like:
```
voice/
└── vosk_model/
    └── vosk-model-small-en-us-0.15/
        ├── am/
        ├── conf/
        ├── graph/
        └── ...
```

---

#### Step 8 — Install Piper TTS (Luna's Voice)

Piper is a fast, free, offline text-to-speech engine. Luna will use this to speak!

1. Go to 👉 https://github.com/rhasspy/piper/releases
2. Download the latest Windows release: `piper_windows_amd64.zip`
3. Unzip it
4. Place the `piper.exe` file somewhere on your computer (e.g., `C:\piper\piper.exe`)
5. Download a voice model from 👉 https://huggingface.co/rhasspy/piper-voices/tree/main
   - Recommended voice: `en_US-lessac-medium` (sounds natural)
   - Download both the `.onnx` file and the `.onnx.json` file
6. Place both files in `voice/piper_voices/`

> 💡 Piper works differently from most tools — it runs as a command-line program. Your Python code will call it like a system command. We'll set this up in Phase 5!

---

#### Step 9 — Get Your Gemini API Key 🔑

1. Go to 👉 https://aistudio.google.com/
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key (it looks like: `AIzaSy...`)

Now open your `.env` file (in your project root) and add:
```
GEMINI_API_KEY=AIzaSy_your_actual_key_here
```

> ⚠️ **NEVER** put your API key directly in your Python code.
> ⚠️ **NEVER** upload your `.env` file to GitHub.
> ✅ The `python-dotenv` library will read it safely for you.

> 💡 **Backup Plan (Groq API)**: If Gemini doesn't work, go to https://console.groq.com/ and get a free Groq API key. Add it as `GROQ_API_KEY=your_key_here`. Groq runs fast LLMs like Llama 3 for free!

---

### 📁 Files Created in This Phase

| File | Purpose |
|------|---------|
| `requirements.txt` | Lists all Python packages |
| `.env` | Stores your secret API key |
| `python/config.py` | Will load settings (Phase 2) |
| All empty folders | Structure for future phases |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Skipping "Add Python to PATH" | Python commands won't work in terminal | Reinstall Python, check the box |
| Forgetting to activate `luna_env` | Wrong Python version used | Always run `luna_env\Scripts\activate` first |
| Putting API key in Python file | Huge security risk if you share code | Use `.env` file always |
| Installing packages globally | Conflicts with other projects | Only install inside `luna_env` |
| Skipping Vosk model download | Voice won't work at all | Model must be in the right folder |

---

### ✅ How to Know You Did It Right

Run these checks in your terminal (with `luna_env` active):

```
python --version          # Should show Python 3.11.x
pip list                  # Should show all installed packages
```

Also verify your folder structure exists by opening File Explorer and checking:
```
C:\Users\HP\Documents\AI Plant Monitor\
```

You should see all the folders: `arduino/`, `python/`, `data/`, `voice/`, `dashboard/`

And your `.env` file should contain your API key.

---

### 🎊 Phase 1 Celebration!

If everything above is done — **you just built the foundation of Luna's world!** 🌱

You've installed professional development tools, set up a clean isolated environment, organized your project like a real software engineer, and secured your API credentials properly.

That's not beginner stuff — that's what real developers do every day. You should feel great about this!

---

## ⏸️ STOP HERE

> 👉 Take your time with Phase 1. Don't rush.
> 
> When you're done, type: **"Phase 1 done"** or **"Next"**
> 
> I'll then give you **Phase 2: Arduino + Sensors** 🔌

---

## 📌 Quick Reference (Save This!)

| Tool | Purpose | Download Link |
|------|---------|---------------|
| Python 3.11 | Run all AI/Python code | python.org/downloads |
| Arduino IDE 2 | Program your Arduino | arduino.cc/en/software |
| VS Code | Write Python code | code.visualstudio.com |
| Vosk model | Offline speech recognition | alphacephei.com/vosk/models |
| Piper TTS | Luna's voice | github.com/rhasspy/piper/releases |
| Gemini API | AI reasoning cloud | aistudio.google.com |
| Groq API | Backup AI (free) | console.groq.com |

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 1 of 10*
