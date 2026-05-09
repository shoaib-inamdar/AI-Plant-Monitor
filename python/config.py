import os
from dotenv import load_dotenv

# Find the project root (one level up from this config.py file)
# This ensures .env is always found even when imported from different locations
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, ".env"))


SERIAL_PORT="SIMULATED"
BAUD_RATE=9600
READ_INTERVAL_SECONDS=2

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

AI_MODEL="gemini-2.5-flash"
USE_BACKUP_AI=False

TEMP_MIN = 0         # °C — below this is definitely wrong
TEMP_MAX = 50        # °C — above this is definitely wrong
HUM_MIN = 10         # %
HUM_MAX = 100        # %
AQI_MIN = 200        # ppm
AQI_MAX = 3000       # ppm
PRES_MIN = 900       # hPa
PRES_MAX = 1100      # hPa

CSV_LOG_PATH = "data/sensor_logs/sensor_data.csv"
MEMORY_FILE_PATH = "data/luna_memory.json"

AI_CALL_INTERVAL=30
MAX_RETRIES=3
# voice settings #

# path to piper executable 
PIPER_EXE_PATH = r"C:\piper\piper.exe"

# path to Piper voice model
PIPER_VOICE_MODEL = "voice/piper_voices/en_US-lessac-medium.onnx"

# path to Vosk speech recognition model
VOSK_MODEL_PATH = "voice/vosk_model/vosk-model-small-en-us-0.15"

# audio settings  #

# sample rate for microphone input (vosk expects 16000 Hz)
AUDIO_SAMPLE_RATE = 16000

# size of each audio chunk read from mic
AUDIO_CHUNK_SIZE = 4096

# maximum time to listen before stopping
LISTEN_TIMEOUT_SECONDS = 10