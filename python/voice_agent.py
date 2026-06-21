import sys
import os
import json
import subprocess
import threading
import time

# UTF-8 fix (must be first)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── TTS BACKEND SELECTION ─────────────────────────────────────────────────────
# Primary:  pyttsx3   — uses Windows SAPI5 (no DLLs, no PyAudio, always works)
# Fallback: Piper TTS — offline neural voice (needs piper.exe + DLLs + PyAudio)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False

# ── CONFIG IMPORT ─────────────────────────────────────────────────────────────
try:
    from python.config import (
        AUDIO_CHUNK_SIZE, AUDIO_SAMPLE_RATE, LISTEN_TIMEOUT_SECONDS,
        PIPER_EXE_PATH, PIPER_VOICE_MODEL, VOSK_MODEL_PATH,
        VOICE_ENABLED, TTS_BACKEND, TTS_RATE, TTS_VOLUME,
    )
except ImportError:
    from config import (
        AUDIO_CHUNK_SIZE, AUDIO_SAMPLE_RATE, LISTEN_TIMEOUT_SECONDS,
        PIPER_EXE_PATH, PIPER_VOICE_MODEL, VOSK_MODEL_PATH,
        VOICE_ENABLED, TTS_BACKEND, TTS_RATE, TTS_VOLUME,
    )


# ── PYTTSX3 TTS (PRIMARY — zero dependencies beyond pip install) ──────────────
class Pyttsx3TTS:
    """
    Uses Windows built-in SAPI5 voices via pyttsx3.
    No DLL files, no PyAudio, no Piper needed.
    Works immediately on any Windows machine.
    """

    def __init__(self):
        self.available = False
        self._engine   = None  # lazy-init: create engine per call (thread-safe)

        if not PYTTSX3_AVAILABLE:
            print("⚠️  pyttsx3 not installed — run: uv add pyttsx3")
            return
        if not VOICE_ENABLED:
            print("🔇 Voice disabled in config (VOICE_ENABLED=False)")
            return

        # Quick smoke test
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate",   TTS_RATE)
            engine.setProperty("volume", TTS_VOLUME)
            # Try to pick a female voice (sounds better for Luna)
            voices = engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.stop()
            self.available = True
            print("🔊 pyttsx3 TTS ready (Windows SAPI5)")
        except Exception as e:
            print(f"⚠️  pyttsx3 init failed: {e}")

    def speak(self, text):
        if not text or not self.available:
            if text:
                print(f"[TTS] {text}")
            return

        # Each call creates a fresh engine — avoids thread-state issues
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate",   TTS_RATE)
            engine.setProperty("volume", TTS_VOLUME)
            voices = engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            print("🔊 Luna spoke")
        except Exception as e:
            print(f"⚠️  TTS error: {e}")
            print(f"[TTS fallback] {text}")


# ── PIPER TTS (OPTIONAL NEURAL FALLBACK) ─────────────────────────────────────
class PiperTTS:
    """
    High-quality neural voice using local Piper binary.
    Requires: piper.exe + libonnxruntime.dll + .onnx voice model + PyAudio.
    Falls back gracefully to console print if any piece is missing.
    """

    def __init__(self):
        self.available = False
        if not VOICE_ENABLED:
            return
        if not os.path.isfile(PIPER_EXE_PATH):
            print(f"⚠️  Piper not found at {PIPER_EXE_PATH}")
            return
        if not os.path.isfile(PIPER_VOICE_MODEL):
            print(f"⚠️  Voice model not found at {PIPER_VOICE_MODEL}")
            return
        if not PYAUDIO_AVAILABLE:
            print("⚠️  PyAudio not installed — Piper voice disabled")
            return
        self.available = True
        print("🔊 Piper TTS ready (neural voice)")

    def speak(self, text):
        if not text or not self.available:
            if text and not PYTTSX3_AVAILABLE:
                print(f"[TTS] {text}")
            return
        try:
            result = subprocess.run(
                [PIPER_EXE_PATH, "--model", PIPER_VOICE_MODEL, "--output-raw"],
                input=text.encode("utf-8"), capture_output=True, timeout=30,
            )
            audio_bytes = result.stdout
            if not audio_bytes:
                print("⚠️  Piper produced no audio — check DLLs in piper/ folder")
                return
            pa     = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paInt16, channels=1, rate=22050, output=True)
            stream.write(audio_bytes)
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print("🔊 Luna spoke (Piper)")
        except subprocess.TimeoutExpired:
            print("⚠️  Piper timed out")
        except Exception as e:
            print(f"⚠️  Piper error: {e}")


# ── VOSK STT ──────────────────────────────────────────────────────────────────
class VoskSTT:
    """
    Offline speech-to-text using Vosk + kaldi model.
    Falls back to keyboard input if unavailable.
    """

    def __init__(self):
        self.available = False

        if not VOICE_ENABLED:
            return
        if not os.path.isdir(VOSK_MODEL_PATH):
            print(f"⚠️  Vosk model not found at {VOSK_MODEL_PATH}")
            return
        if not PYAUDIO_AVAILABLE:
            print("⚠️  PyAudio not installed — STT mic input disabled")
            return

        try:
            import vosk
            import logging
            # Suppress Vosk's verbose kaldi logs
            logging.getLogger("vosk").setLevel(logging.WARNING)
            self.model      = vosk.Model(VOSK_MODEL_PATH)
            self.recognizer = vosk.KaldiRecognizer(self.model, AUDIO_SAMPLE_RATE)
            self.available  = True
            print("🎙️  Vosk STT ready")
        except Exception as e:
            print(f"⚠️  Vosk setup failed: {e}")

    def listen(self):
        if not self.available or not PYAUDIO_AVAILABLE:
            print("🎙️  [Type your message]: ", end="")
            return input().strip()

        pa = pyaudio.PyAudio()
        stream = None
        try:
            stream = pa.open(
                format=pyaudio.paInt16, channels=1,
                rate=AUDIO_SAMPLE_RATE, input=True,
                frames_per_buffer=AUDIO_CHUNK_SIZE,
            )
            print("🎙️  Listening...")
            start     = time.time()
            final_txt = ""
            while (time.time() - start) < LISTEN_TIMEOUT_SECONDS:
                chunk = stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(chunk):
                    res  = json.loads(self.recognizer.Result())
                    text = res.get("text", "").strip()
                    if text:
                        final_txt = text
                        print(f"✅ Heard: {text}")
                        break
            if not final_txt:
                print("⏰ Timeout — nothing detected")
            return final_txt
        except Exception as e:
            print(f"⚠️  STT error: {e}")
            return ""
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            pa.terminate()


# ── LUNA VOICE AGENT ──────────────────────────────────────────────────────────
class LunaVoice:
    """
    High-level voice interface. Automatically picks the best available TTS:
      1. pyttsx3 (always works on Windows, no setup needed)
      2. Piper   (neural quality, needs full binary + PyAudio)
    STT uses Vosk or falls back to keyboard.
    """

    def __init__(self):
        # Determine which TTS to use based on config + availability
        self._tts = self._init_tts()
        self.stt  = VoskSTT()
        print("🌿 Luna Voice Agent ready")

    def _init_tts(self):
        backend = TTS_BACKEND.lower()

        if backend == "pyttsx3":
            t = Pyttsx3TTS()
            if t.available:
                return t
            # Auto-fallback to Piper
            print("⚠️  pyttsx3 failed — trying Piper...")
            p = PiperTTS()
            return p

        elif backend == "piper":
            p = PiperTTS()
            if p.available:
                return p
            # Auto-fallback to pyttsx3
            print("⚠️  Piper failed — falling back to pyttsx3...")
            t = Pyttsx3TTS()
            return t

        else:
            print(f"⚠️  Unknown TTS_BACKEND '{backend}' — defaulting to pyttsx3")
            return Pyttsx3TTS()

    def speak(self, text):
        """Speak text. Non-blocking — runs in background thread."""
        if not text or not VOICE_ENABLED:
            if text:
                print(f"[Voice disabled] {text}")
            return
        thread = threading.Thread(target=self._tts.speak, args=(text,), daemon=True)
        thread.start()

    def speak_sync(self, text):
        """Speak text and WAIT until finished (blocking)."""
        if not text or not VOICE_ENABLED:
            return
        self._tts.speak(text)

    def listen(self):
        return self.stt.listen()

    def speak_response(self, response_dict):
        """Speak Luna's AI response message."""
        if not response_dict:
            return
        message = response_dict.get("message", "")
        reason  = response_dict.get("reason",  "")
        text    = f"{message}. {reason}" if (message and reason) else (message or reason)
        if not text:
            text = "I am monitoring my environment carefully."
        self.speak(text)


# ── STANDALONE TEST ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌿 Testing Luna Voice Agent\n")
    voice = LunaVoice()

    print("\n--- TTS Test ---")
    voice.speak_sync("Hello! I am Luna, your plant friend. I am feeling wonderful today!")
    print("TTS test complete.\n")

    ans = input("Test speech recognition? (y/n): ").strip().lower()
    if ans == "y":
        print("\n--- STT Test ---")
        print("Say something...")
        heard = voice.listen()
        if heard:
            print(f"You said: '{heard}'")
            voice.speak_sync(f"I heard you say: {heard}")
        else:
            print("Nothing detected.")

    print("\n✅ Voice agent test complete!")
