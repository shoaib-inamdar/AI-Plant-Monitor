# 🌱 Luna — Phase 5: Luna's Voice (Piper TTS + Vosk STT)
### Teaching Luna to Speak and Listen 🎙️🔊

> **Remember**: Read the pseudocode carefully, understand it, then write the Python yourself. Voice coding is genuinely exciting — Luna will literally talk to you by the end of this phase!

---

## 🎉 Phase 4 Check — You Passed!

Here's what was found and fixed:

| Check | Status | Note |
|-------|--------|------|
| `google.genai` import (updated SDK) | ✅ | Using `genai.Client()` — correct for new SDK |
| `_build_prompt()` | ✅ | Clean formatted string, all fields used |
| `analyse()` retry loop | ✅ | Works correctly |
| JSON markdown stripping (`\`\`\`json`) | ✅ | Handles Gemini markdown wrapping |
| `format_response()` with emoji indicators | ✅ | 🟢 🟡 🔴 based on score |
| `explain_decision()` | ✅ | Clean readable output |
| Missing `except Exception` in retry loop | 🔧 Fixed | API/network errors now trigger retries too |
| `main.py` printed raw dict | 🔧 Fixed | Now uses `brain.format_response(response)` |
| UTF-8 emoji crash | 🔧 Fixed | Added fix to top of `ai_brain.py` too |
| `main.py` import ordering | 🔧 Fixed | UTF-8 fix now runs before any imports |

Luna is thinking correctly. Now let's give her a voice! 🌿

---

## ✅ Phase 5 — Luna's Voice Agent

> **Stop after this phase and tell me "Phase 5 done" when finished!**

---

### 🎯 Goal

Build `python/voice_agent.py` with two abilities:

1. **Text-to-Speech (TTS)** — Luna speaks her responses out loud using **Piper**
2. **Speech-to-Text (STT)** — Luna listens to your voice using **Vosk**

By the end, you can:
- Ask Luna a question out loud → she hears you → AI responds → she speaks back
- It all runs offline — no cloud needed for voice (only Gemini for reasoning)

---

### 🤔 Why This Phase Matters

Reading sensor data in a terminal is useful. But a plant that **speaks to you** is magical. 🌿

More practically, voice interaction means:
- You don't need to look at a screen to check on Luna
- You can ask "Luna, how are you feeling?" while watering and she'll reply
- Later (Phase 8), Luna can alert you verbally: "I'm thirsty! Please water me!"

This is also where your project moves from "coding exercise" to "actual product."

---

### 🧠 Four Concepts to Understand First

#### 1. What is a Subprocess?
Piper is a separate program — it's not a Python library. It's an `.exe` file.

To use it from Python, you call it like a terminal command using `subprocess`:
```python
import subprocess
subprocess.run(["piper.exe", "--model", "voice.onnx", "--output_file", "out.wav"])
```

You can also pipe text into Piper via stdin (standard input):
```python
process = subprocess.run(
    ["piper.exe", "--model", "voice.onnx", "--output-raw"],
    input=b"Hello I am Luna",
    capture_output=True
)
```
This is exactly what you'll do — send Luna's text to Piper, get audio bytes back.

#### 2. What is PyAudio?
PyAudio is a Python library for playing and recording audio. You'll use it to:
- Play the audio bytes that Piper outputs
- Record microphone input for Vosk

PyAudio talks to your sound card at a low level using something called **streams**. A stream is like an open pipe of audio data flowing in or out.

#### 3. How Vosk Works
Vosk is an offline speech recognition library. You give it:
1. A language model (the folder you downloaded in Phase 1)
2. Audio bytes from your microphone

It returns JSON results like:
```json
{"text": "luna how are you feeling"}
```

Vosk processes audio in **chunks** (small pieces at a time), not the whole recording at once. This lets it start recognising words while you're still speaking — real-time processing.

#### 4. What is a KaldiRecognizer?
This is Vosk's main object. You create it with:
- The loaded model
- The sample rate (usually 16000 Hz for speech)

Then you feed it audio chunks:
```python
if recognizer.AcceptWaveform(audio_chunk):
    result = json.loads(recognizer.Result())
    # result["text"] is the full recognised phrase
```

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Install PyAudio

You need PyAudio to play audio and record from the microphone.

> ⚠️ PyAudio can be tricky on Windows. Use this command:
```
uv add pyaudio
```

If that fails with a build error, try:
```
uv add pipwin
uv run pipwin install pyaudio
```

Or download the wheel directly from:
👉 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Choose `PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl` (for Python 3.11, 64-bit).
Then install with: `uv pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl`

> 💡 You are using Python 3.14 (from your pyproject.toml). Check which version you have with `python --version` and pick the matching wheel.

---

#### Step 2 — Verify Your Piper Setup

Before coding, make sure Piper is ready.

Check if you have these files from Phase 1:
```
voice/
└── piper_voices/
    ├── en_US-lessac-medium.onnx      ← the voice model
    └── en_US-lessac-medium.onnx.json ← the config file
```

And `piper.exe` somewhere on your system (e.g., `C:\piper\piper.exe`).

Test Piper manually from your terminal:
```
echo "Hello I am Luna your plant friend" | C:\piper\piper.exe --model "voice\piper_voices\en_US-lessac-medium.onnx" --output_file test_output.wav
```

Then open `test_output.wav` — you should hear a voice!

> If it works, great. If you don't have Piper yet, download it now from:
> 👉 https://github.com/rhasspy/piper/releases

---

#### Step 3 — Verify Your Vosk Model Setup

Check that your Vosk model folder is in the right place:
```
voice/
└── vosk_model/
    └── vosk-model-small-en-us-0.15/
        ├── am/
        ├── conf/
        ├── graph/
        └── ...
```

Test Vosk is importable:
```
uv run python -c "import vosk; print('Vosk OK')"
```

You should see: `Vosk OK`

---

#### Step 4 — Update `config.py`

Add these settings at the bottom of your config:

```
PSEUDOCODE — add to config.py:

# Voice settings
PIPER_EXE_PATH = r"C:\piper\piper.exe"     # Path to piper.exe (change if yours is different)
PIPER_VOICE_MODEL = "voice/piper_voices/en_US-lessac-medium.onnx"

VOSK_MODEL_PATH = "voice/vosk_model/vosk-model-small-en-us-0.15"

AUDIO_SAMPLE_RATE = 16000    # 16kHz — standard for speech recognition
AUDIO_CHUNK_SIZE = 4096      # How many audio bytes to read at a time
LISTEN_TIMEOUT_SECONDS = 10  # How long to listen before giving up
```

> 💡 Make sure `PIPER_EXE_PATH` matches where you actually put `piper.exe` on your computer!

---

#### Step 5 — Build `python/voice_agent.py`

This is the main file for Phase 5. It has two classes plus a wrapper.

```
PSEUDOCODE for voice_agent.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: sys, os, json, subprocess, time, wave, io, threading
Import: pyaudio
Try the dual-import pattern for config values:
    Try: from python.config import PIPER_EXE_PATH, PIPER_VOICE_MODEL, VOSK_MODEL_PATH,
                                   AUDIO_SAMPLE_RATE, AUDIO_CHUNK_SIZE, LISTEN_TIMEOUT_SECONDS
    Except ImportError: from config import ...

--- UTF-8 FIX (same as other files) ---
At the very top (before imports), add the sys.stdout.reconfigure fix

--- CLASS: PiperTTS ---
Purpose: Converts text to speech using Piper

  __init__(self):
    Check if the piper.exe file actually exists:
      Use os.path.isfile(PIPER_EXE_PATH)
      If it doesn't exist:
        Print a warning: f"⚠️ Piper not found at {PIPER_EXE_PATH}"
        Set self.available = False
      Else:
        Set self.available = True
        Print: f"🔊 Piper TTS ready"
    
    Check if the voice model file exists too:
      If PIPER_VOICE_MODEL doesn't exist:
        Print: f"⚠️ Voice model not found at {PIPER_VOICE_MODEL}"
        Set self.available = False

  ---

  speak(self, text):
    Purpose: Say the given text out loud using Piper
    
    If not self.available:
      Print: f"[TTS unavailable] Luna would say: {text}"
      Return   ← graceful fallback, don't crash
    
    If text is empty or None: return
    
    Try:
      Step 1: Build the command list:
        command = [
            PIPER_EXE_PATH,
            "--model", PIPER_VOICE_MODEL,
            "--output-raw"          ← tells Piper to output raw PCM audio bytes
        ]
      
      Step 2: Run Piper as a subprocess:
        result = subprocess.run(
            command,
            input=text.encode("utf-8"),   ← send the text to Piper's stdin
            capture_output=True,          ← capture the audio output
            timeout=30                    ← don't wait forever
        )
      
      Step 3: Get the raw audio bytes:
        audio_bytes = result.stdout
        
        If audio_bytes is empty:
          Print: "⚠️ Piper produced no audio"
          Return
      
      Step 4: Play the audio bytes using PyAudio:
        audio = pyaudio.PyAudio()
        
        Open a stream:
        stream = audio.open(
            format=pyaudio.paInt16,      ← 16-bit audio (matches Piper output)
            channels=1,                  ← mono
            rate=22050,                  ← Piper outputs at 22050 Hz by default
            output=True                  ← this is a playback stream
        )
        
        Write all audio bytes to the stream at once:
        stream.write(audio_bytes)
        
        Close stream and terminate PyAudio:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        Print: "🔊 Luna spoke"
    
    Except subprocess.TimeoutExpired:
      Print: "⚠️ Piper timed out"
    
    Except Exception as error:
      Print: f"⚠️ TTS error: {error}"

--- CLASS: VoskSTT ---
Purpose: Listens to microphone and converts speech to text using Vosk

  __init__(self):
    Check if the Vosk model folder exists:
      Use os.path.isdir(VOSK_MODEL_PATH)
      If not found:
        Print: f"⚠️ Vosk model not found at {VOSK_MODEL_PATH}"
        Set self.available = False
        Return
    
    Try:
      Import vosk (inside try — in case vosk isn't installed)
      
      Load the model:
        self.model = vosk.Model(VOSK_MODEL_PATH)
      
      Create the recogniser:
        self.recognizer = vosk.KaldiRecognizer(self.model, AUDIO_SAMPLE_RATE)
      
      Set self.available = True
      Print: "🎙️ Vosk STT ready"
    
    Except Exception as error:
      Print: f"⚠️ Vosk setup failed: {error}"
      Set self.available = False

  ---

  listen(self):
    Purpose: Record microphone input until silence, return recognised text
    
    If not self.available:
      Print: "[STT unavailable] Type your message instead:"
      Return input().strip()    ← fallback to keyboard input!
    
    audio = pyaudio.PyAudio()
    
    Try:
      Open a microphone stream:
      stream = audio.open(
          format=pyaudio.paInt16,
          channels=1,
          rate=AUDIO_SAMPLE_RATE,
          input=True,                    ← this is a recording stream
          frames_per_buffer=AUDIO_CHUNK_SIZE
      )
      
      Print: "🎙️ Listening... (speak now)"
      
      Set start_time = time.time()
      Set final_text = ""
      
      Loop while (time.time() - start_time) < LISTEN_TIMEOUT_SECONDS:
        Read a chunk of audio:
          chunk = stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)
        
        Feed chunk to Vosk:
          If self.recognizer.AcceptWaveform(chunk):
            ← This returns True when a full phrase is detected
            
            Get the result:
              result = json.loads(self.recognizer.Result())
              text = result.get("text", "").strip()
            
            If text is not empty:
              final_text = text
              Print: f"✅ Heard: {text}"
              Break   ← stop listening once we have a result
      
      If final_text is empty:
        Print: "⏰ Listening timed out — nothing detected"
      
      Return final_text
    
    Except Exception as error:
      Print: f"⚠️ STT error: {error}"
      Return ""
    
    Finally:  ← always runs, even if there's an error
      Try to close stream and terminate audio (cleanup)

--- CLASS: LunaVoice ---
Purpose: Wraps both TTS and STT into one easy interface

  __init__(self):
    self.tts = PiperTTS()
    self.stt = VoskSTT()
    Print: "🌿 Luna Voice Agent ready"
  
  speak(self, text):
    ← Just calls self.tts.speak(text)
  
  listen(self):
    ← Just calls self.stt.listen()
  
  speak_response(self, response_dict):
    Purpose: Given a Gemini response dict, build a speech-friendly version and say it
    
    If response_dict is None: return
    
    Build a short speech string (not the full JSON — just the key parts):
      speech_text = f"{response_dict['message']}. {response_dict['reason']}"
    
    ← Keep it short! Long text takes too long to synthesise
    
    self.speak(speech_text)

--- MAIN BLOCK (if __name__ == "__main__") ---
Purpose: Test voice agent standalone

Steps:
  1. Create a LunaVoice instance
  2. Print: "Testing Luna's voice..."
  
  # Test TTS first
  3. Call: voice.speak("Hello! I am Luna, your plant friend. I am feeling great today!")
  4. Print: "Speech test complete"
  
  # Test STT (optional — only if microphone is available)
  5. Ask user: "Do you want to test speech recognition? (y/n)"
  6. If yes:
       Print: "Say something to Luna..."
       text = voice.listen()
       If text:
         Print: f"You said: {text}"
         voice.speak(f"I heard you say: {text}")
       Else:
         Print: "Nothing was detected"
```

---

#### Step 6 — Update `main.py` to Use Luna's Voice

Add voice to the main loop:

```
PSEUDOCODE — additions to main.py:

--- NEW IMPORTS ---
Add: from python.voice_agent import LunaVoice

--- IN main() FUNCTION ---
After creating brain, also create:
  voice = LunaVoice()

After printing the AI response, also speak it:
  if response is not None:
    print(brain.format_response(response))
    voice.speak_response(response)    ← Luna speaks her assessment!
    last_ai_call_time = current_time
```

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/voice_agent.py` | New — TTS + STT + LunaVoice wrapper |
| `python/config.py` | Added voice paths and audio settings |
| `main.py` | Luna now speaks her AI assessments |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Hardcoding the Piper path | Breaks on different computers | Always use the config variable |
| Not checking `self.available` before using | Crashes if Piper/Vosk not installed | Always check availability first |
| Forgetting `.encode("utf-8")` when sending text to Piper | subprocess expects bytes, not str | Add `.encode("utf-8")` to the input |
| Using rate=44100 for PyAudio playback of Piper | Piper outputs at 22050 Hz — wrong rate = chipmunk voice | Use rate=22050 for playback |
| Using rate=22050 for Vosk recording | Vosk needs 16000 Hz — wrong rate = garbled recognition | Use AUDIO_SAMPLE_RATE (16000) for recording |
| Not closing the PyAudio stream | Memory leak, mic stays locked | Always use `finally:` block to close |
| Making speech text too long | Piper takes 10+ seconds for long text | Keep speech under 2 sentences |

---

### 💡 Tips and Tricks

**Testing TTS without a microphone:**
You can test Piper alone without any microphone — just run the main block and skip the STT test.

**Making Luna's voice shorter:**
In `speak_response()`, you can make the speech even shorter:
```
Only say the message field, not the reason:
speech_text = response_dict['message']
```
Try both and see what feels more natural.

**Vosk model path on Windows:**
Make sure the path in config uses raw strings or forward slashes to avoid backslash issues:
```python
VOSK_MODEL_PATH = r"voice\vosk_model\vosk-model-small-en-us-0.15"
# OR
VOSK_MODEL_PATH = "voice/vosk_model/vosk-model-small-en-us-0.15"
```

**If PyAudio won't install:**
Try this — it works for most Windows Python setups:
```
uv pip install pyaudio --find-links https://github.com/intxcc/pyaudio_portaudio/releases
```

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/voice_agent.py` runs without crashing
- [ ] Luna's voice plays through your speakers (you hear "Hello I am Luna...")
- [ ] The TTS class prints `[TTS unavailable] Luna would say: ...` if Piper isn't found (graceful fallback)
- [ ] The STT class falls back to keyboard input if Vosk model isn't found
- [ ] `uv run python main.py` plays Luna's voice assessment after the first 30 seconds
- [ ] Pressing Ctrl+C exits cleanly

---

### 🎊 Phase 5 Celebration (when you're done!)

🌟 **Luna has a voice now!**

You just built an offline voice system from scratch, integrating:
- A TTS engine (Piper) via subprocess piping
- An STT engine (Vosk) with real-time microphone streaming
- A graceful fallback system (keyboard input when hardware is missing)
- A voice interface layer that the rest of the system calls cleanly

This is the same architecture used in Amazon Alexa, Google Home, and Siri — sensor input → AI processing → voice response. The difference is yours runs locally on your laptop. Seriously impressive! 🌱

---

## ⏸️ STOP HERE

> 👉 Build `voice_agent.py`, update `config.py` and `main.py`
>
> Test Piper TTS first, then test Vosk STT
>
> When you're done, type: **"Phase 5 done"** or **"Next"**
>
> I'll then give you **Phase 6: Memory & Data** 💾

---

## 📊 Project Progress

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  ✅ Serial bridge — data pipeline
Phase 4  ✅ AI Brain — Luna thinks
Phase 5  🔨 You are here — Luna's Voice
Phase 6  ⏳ Memory & Data
Phase 7  ⏳ Health Scoring
Phase 8  ⏳ Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **50% done** with the full project. Halfway there — and already one of the most impressive beginner projects around! 🌿

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 5 of 10*
