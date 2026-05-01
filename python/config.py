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

AI_MODEL="gemini-1.5-flash"
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
