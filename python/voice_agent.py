import sys

# UTF-8 fix (must be first)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import subprocess
import time

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False
    print("⚠️  pyaudio not installed — voice playback/recording unavailable")
    print("   Install with: uv pip install pipwin && uv run pipwin install pyaudio")

try:
    from python.config import (
        AUDIO_CHUNK_SIZE,
        AUDIO_SAMPLE_RATE,
        LISTEN_TIMEOUT_SECONDS,
        PIPER_EXE_PATH,
        PIPER_VOICE_MODEL,
        VOSK_MODEL_PATH,
    )
except ImportError:
    # pyrefly: ignore [missing-import]
    from config import (
        AUDIO_CHUNK_SIZE,
        AUDIO_SAMPLE_RATE,
        LISTEN_TIMEOUT_SECONDS,
        PIPER_EXE_PATH,
        PIPER_VOICE_MODEL,
        VOSK_MODEL_PATH,
    )


class PiperTTS:
    def __init__(self):
        self.available = True

        if not os.path.isfile(PIPER_EXE_PATH):
            print(f"⚠️ Piper not found at {PIPER_EXE_PATH}")
            self.available = False

        if not os.path.isfile(PIPER_VOICE_MODEL):
            print(f"⚠️ Voice model not found at {PIPER_VOICE_MODEL}")
            self.available = False

        if self.available:
            print("🔊 Piper TTS ready")

    def speak(self, text):
        if not text:
            return

        if not self.available:
            print(f"[TTS unavailable] {text}")
            return

        if not PYAUDIO_AVAILABLE:
            print(f"[Audio unavailable] Luna would say: {text}")
            return

        try:
            result = subprocess.run(
                [PIPER_EXE_PATH, "--model", PIPER_VOICE_MODEL, "--output-raw"],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            audio_bytes = result.stdout
            if not audio_bytes:
                print("⚠️ Piper produced no audio — check DLL files in piper/ folder")
                return

            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16, channels=1, rate=22050, output=True
            )
            stream.write(audio_bytes)
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print("🔊 Luna spoke")

        except subprocess.TimeoutExpired:
            print("⚠️ Piper timed out")
        except Exception as e:
            print(f"⚠️ TTS error: {e}")


class VoskSTT:
    def __init__(self):
        self.available = False

        if not os.path.isdir(VOSK_MODEL_PATH):
            print(f"⚠️ Vosk model not found at {VOSK_MODEL_PATH}")
            return

        try:
            import vosk

            self.model = vosk.Model(VOSK_MODEL_PATH)
            self.recognizer = vosk.KaldiRecognizer(self.model, AUDIO_SAMPLE_RATE)

            self.available = True
            print("🎙️ Vosk STT ready")

        except Exception as e:
            print(f"⚠️ Vosk setup failed: {e}")

    def listen(self):
        if not self.available:
            print("[STT unavailable] Type instead:")
            return input().strip()

        if not PYAUDIO_AVAILABLE:
            print("[Audio unavailable] Type your message instead:")
            return input().strip()

        pa = pyaudio.PyAudio()
        stream = None

        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=AUDIO_SAMPLE_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK_SIZE,
            )

            print("🎙️ Listening...")
            start_time = time.time()
            final_text = ""

            while (time.time() - start_time) < LISTEN_TIMEOUT_SECONDS:
                chunk = stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)

                if self.recognizer.AcceptWaveform(chunk):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        final_text = text
                        print(f"✅ Heard: {text}")
                        break

            if not final_text:
                print("⏰ Timeout — nothing detected")

            return final_text

        except Exception as e:
            print(f"⚠️ STT error: {e}")
            return ""

        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            pa.terminate()


class LunaVoice:
    def __init__(self):
        self.tts = PiperTTS()
        self.stt = VoskSTT()
        print("🌿 Luna Voice Agent ready")

    def speak(self, text):
        self.tts.speak(text)

    def listen(self):
        return self.stt.listen()

    def speak_response(self, response_dict):
        if not response_dict:
            return

        message = response_dict.get("message", "")
        reason = response_dict.get("reason", "")

        if message and reason:
            speech_text = f"{message}. {reason}"
        else:
            speech_text = message or reason

        if not speech_text:
            speech_text = "I have nothing to say right now."

        self.speak(speech_text)


if __name__ == "__main__":
    print("🌿 Testing Luna Voice Agent\n")

    voice = LunaVoice()

    # --- Test TTS ---
    print("\n--- TTS Test ---")
    voice.speak("Hello! I am Luna, your plant friend. I am feeling wonderful today!")
    print("TTS test done.\n")

    # --- Test STT (optional) ---
    answer = input("Test speech recognition too? (y/n): ").strip().lower()
    if answer == "y":
        print("\n--- STT Test ---")
        print("Say something to Luna...")
        heard = voice.listen()
        if heard:
            print(f"You said: '{heard}'")
            voice.speak(f"I heard you say: {heard}")
        else:
            print("Nothing detected.")
    else:
        print("Skipping STT test.")

    print("\n✅ Voice agent test complete!")
