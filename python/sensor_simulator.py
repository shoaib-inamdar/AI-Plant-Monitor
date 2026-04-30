import os, random, time, csv
from datetime import datetime


folder_path="data/sensor_logs/"
file_path="data/sensor_logs/sensor_data.csv"

def generate_sensor_reading():
    current_hour=datetime.now().hour
    
    #Temperature
    base_temp=22

    if 10 <= current_hour <= 17:
        temperature=round( base_temp + random.uniform(3 , 6), 1)
    else:
        temperature=round(base_temp - random.uniform(0 , 2),1)

    # Humidity
    base_humidity = 60

    if temperature > 28:
        humidity = base_humidity - random.uniform(1, 3)
    elif temperature < 22:
        humidity = base_humidity + random.uniform(1, 3)
    else:
        humidity = base_humidity

    # Add small noise
    humidity += random.uniform(-3, 3)

    # Clamp between 20 and 95
    humidity = max(20, min(humidity, 95))
    humidity = round(humidity, 1)

    # Air Quality
    base_aqi=420
    aqi=int( base_aqi+ random.randint(-80 , + 80))

    # Rain
    rain_value= random.random()
    if rain_value< 0.10:
        rain=1
    else:
        rain=0

    # Pressure
    pressure_base=1013.25
    pressure=round(pressure_base + random.uniform(-5, +5),2)

    #Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pressure = float(f"{pressure:.2f}")  # ensure always 2 decimal places
    readings = {"timestamp":timestamp, "temperature":temperature, "humidity":humidity, "air_quality":aqi, "rain":rain, "pressure":pressure}
    return readings

def reading_to_serial_string(reading):
    temp=reading["temperature"]
    hum=reading["humidity"]
    air = reading["air_quality"]
    rain = reading["rain"]
    pres = reading["pressure"]
    return f"TEMP:{temp},HUM:{hum},AIR:{air},RAIN:{rain},PRES:{pres:.2f}"


def save_to_csv(reading):
    os.makedirs(folder_path, exist_ok=True)
    
    file_exists=os.path.isfile(file_path)

    fieldnames=["timestamp", "temperature", "humidity", "air_quality", "rain", "pressure"]

    with open(file_path,"a", newline="")as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        
        writer.writerow(reading)

class SimulatedSerial():
    def __init__(self,port="SIMULATED",baudrate=9600):
        self.port=port
        self.baudrate=baudrate
        self.is_open=True
        print(f"🌱 Simulated serial port  active on {self.port}")
    
    def readline(self):
        if not self.is_open:
            return b''
        reading=generate_sensor_reading()
        save_to_csv(reading)
        serial_string = reading_to_serial_string(reading)
        serial_string+="\n"
        reading_in_bytes=serial_string.encode("utf-8")

        time.sleep(2)

        return reading_in_bytes
    
    def close(self):
        self.is_open=False
        print("🔌 Simulated serial port closed")

if __name__ == "__main__":
    s1=SimulatedSerial()
    print("Testing simulator — press Ctrl+C to stop")
    try:

        while True:
            data=s1.readline()
            decoded_data=data.decode("utf-8").strip()
            print(f"[SENSOR] {decoded_data}")
    except KeyboardInterrupt:
        s1.close()
        print("Simulator stopped")
