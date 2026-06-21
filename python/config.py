import os

from dotenv import load_dotenv

# ── PROJECT ROOT ──────────────────────────────────────────────────────────────
# Always resolved relative to this file so paths work from any launch directory
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, ".env"))


# ══════════════════════════════════════════════════════════════════════════════
# HARDWARE TOGGLE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
# Set USE_REAL_HARDWARE=True to read from the Arduino over serial.
# Set USE_REAL_HARDWARE=False to use the built-in sensor simulator.
#
# Per-sensor toggles (only used when USE_REAL_HARDWARE=True):
#   If a particular sensor is not wired up, set its flag to False.
#   Luna will use a safe default value for that sensor instead of
#   crashing or reading garbage from an open pin.
#
USE_REAL_HARDWARE = False  # ← Master switch: False=simulator, True=Arduino

# Individual sensor availability (only matters when USE_REAL_HARDWARE=True)
HW_DHT22_AVAILABLE = True  # Temperature + Humidity (Pin 2)
HW_MQ135_AVAILABLE = True  # Air quality / CO2 (Pin A0)
HW_RAIN_AVAILABLE = True  # Rain sensor (Pin 4)
HW_BMP280_AVAILABLE = True  # Barometric pressure (I2C)
HW_SOIL_AVAILABLE = False  # Capacitive soil moisture (Pin A1) — optional add-on

# Safe defaults used when a sensor is toggled off
DEFAULT_AIR_QUALITY = 450  # ppm — typical clean-indoor reading
DEFAULT_RAIN = 0  # 0=dry
DEFAULT_PRESSURE = 1013.25  # hPa — sea-level standard
DEFAULT_SOIL_MOISTURE = 55  # % — healthy soil moisture


# ══════════════════════════════════════════════════════════════════════════════
# SERIAL / ARDUINO
# ══════════════════════════════════════════════════════════════════════════════
SERIAL_PORT = "COM3"  # Change to your actual COM port (check Arduino IDE)
BAUD_RATE = 9600
READ_INTERVAL_SECONDS = 2


# ══════════════════════════════════════════════════════════════════════════════
# API KEYS
# ══════════════════════════════════════════════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

AI_MODEL = "gemini-2.5-flash"
USE_BACKUP_AI = False
AI_CALL_INTERVAL = 30  # seconds between Gemini API calls
MAX_RETRIES = 3


# ══════════════════════════════════════════════════════════════════════════════
# SENSOR VALIDATION RANGES
# ══════════════════════════════════════════════════════════════════════════════
TEMP_MIN = 0  # °C
TEMP_MAX = 50  # °C
HUM_MIN = 10  # %
HUM_MAX = 100  # %
AQI_MIN = 200  # ppm
AQI_MAX = 3000  # ppm
PRES_MIN = 900  # hPa
PRES_MAX = 1100  # hPa
SOIL_MIN = 0  # % (0=bone dry)
SOIL_MAX = 100  # % (100=waterlogged)


# ══════════════════════════════════════════════════════════════════════════════
# FILE PATHS  (all relative to project root — resolved to absolute at runtime)
# ══════════════════════════════════════════════════════════════════════════════
CSV_LOG_PATH = "data/sensor_logs/sensor_data.csv"
MEMORY_FILE_PATH = "data/luna_memory.json"
CARE_PLAN_FILE = "data/care_plan.json"
INCIDENTS_FILE = "data/incidents.json"


# ══════════════════════════════════════════════════════════════════════════════
# VOICE SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
# VOICE_ENABLED : set False to silence Luna completely (useful in headless mode)
# TTS_BACKEND   : "pyttsx3" (always works) or "piper" (neural, needs setup)
#
VOICE_ENABLED = True
TTS_BACKEND = "pyttsx3"  # "pyttsx3" | "piper"
TTS_RATE = 165  # Words per minute (pyttsx3 only)
TTS_VOLUME = 0.95  # 0.0–1.0 (pyttsx3 only)

# Piper paths (used only when TTS_BACKEND="piper")
PIPER_EXE_PATH = os.path.join(_project_root, "piper", "piper.exe")
PIPER_VOICE_MODEL = os.path.join(
    _project_root, "voice", "piper_voices", "en_US-lessac-medium.onnx"
)

# Vosk STT paths
VOSK_MODEL_PATH = os.path.join(
    _project_root, "voice", "vosk_model", "vosk-model-small-en-us-0.15"
)
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 4096
LISTEN_TIMEOUT_SECONDS = 10


# ══════════════════════════════════════════════════════════════════════════════
# MEMORY / HISTORY
# ══════════════════════════════════════════════════════════════════════════════
MAX_READINGSZ_IN_MEMORY = 100
MAX_AI_RESPONSES_IN_MEMORY = 20
TREND_WINDOW = 10


# ══════════════════════════════════════════════════════════════════════════════
# IDEAL PLANT CONDITIONS  (used by health scorer)
# ══════════════════════════════════════════════════════════════════════════════
IDEAL_TEMP_MIN = 18.0  # °C
IDEAL_TEMP_MAX = 26.0  # °C
IDEAL_HUM_MIN = 50.0  # %
IDEAL_HUM_MAX = 70.0  # %
IDEAL_AQI_MAX = 600  # ppm (lower = better)
IDEAL_SOIL_MIN = 40  # % (below = too dry)
IDEAL_SOIL_MAX = 70  # % (above = too wet)


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH SCORE WEIGHTS  (must sum to 100)
# ══════════════════════════════════════════════════════════════════════════════
WEIGHT_TEMP = 28
WEIGHT_HUM = 22
WEIGHT_SOIL = 20  # Added — soil moisture is the most critical plant signal
WEIGHT_AQI = 15
WEIGHT_RAIN = 10
WEIGHT_PRES = 5
# Total: 28+22+20+15+10+5 = 100 ✓


# ══════════════════════════════════════════════════════════════════════════════
# ALERT THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════
ALERT_TEMP_HIGH = 35.0  # °C
ALERT_TEMP_LOW = 8.0  # °C
ALERT_HUM_LOW = 20.0  # %
ALERT_AQI_HIGH = 1200  # ppm
ALERT_SOIL_DRY = 20.0  # % — drought emergency
ALERT_SOIL_WET = 85.0  # % — waterlogging emergency
MAX_SCORE_HISTORY = 50


# ══════════════════════════════════════════════════════════════════════════════
# SCHEDULER
# ══════════════════════════════════════════════════════════════════════════════
MORNING_START = 6
MORNING_END = 10
AFTERNOON_START = 12
AFTERNOON_END = 16
EVENING_START = 18
EVENING_END = 21


# ══════════════════════════════════════════════════════════════════════════════
# SELF-HEALING
# ══════════════════════════════════════════════════════════════════════════════
HEALING_THRESHOLD_SCORE = 60  # Score below this triggers monitoring
HEALING_TRIGGER_COUNT = 5  # Consecutive poor readings before healing mode
HEALING_COOLDOWN_MINUTES = 15  # Min gap between healing plan generations
