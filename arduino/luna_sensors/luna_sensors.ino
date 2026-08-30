```cpp
/*
 * luna_sensors.ino
 * ────────────────────────────────────────────────────────────────
 * Luna AI Plant Care System — ESP32 Sensor Firmware
 *
 * Sends sensor readings as CSV over USB Serial every 2 seconds.
 *
 * CSV Format (one line per reading):
 *   TEMP,HUM,AQI,RAIN,PRESSURE
 *
 * Example:
 *   24.30,62.10,450,0,1013.50
 *
 * Additional sensors:
 *   • Capacitive Soil Moisture Sensor
 *   • LDR Light Sensor
 *   • Rain Sensor Analog Output
 *
 * These additional sensors are displayed on the OLED, while the
 * USB Serial output remains compatible with the existing Luna
 * Python AI system.
 *
 * To use:
 *   1. Upload this sketch to your ESP32 38-pin board
 *   2. In python/config.py set:
 *        SERIAL_PORT = "COM3"   ← your actual ESP32 COM port
 *   3. In main.py set:
 *        reader = SerialReader(use_simulator=False)
 *   That's all — Luna reads the CSV automatically.
 *
 * Wiring Guide:
 * ┌──────────────────────────────┬──────────────────────────────────────┐
 * │ Sensor / Module              │ ESP32 Pin                            │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ DHT22 DATA                   │ GPIO 4                               │
 * │ DHT22 VCC                    │ 3.3V                                 │
 * │ DHT22 GND                    │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ Capacitive Soil Sensor AO    │ GPIO 34 (ADC)                        │
 * │ Capacitive Soil Sensor VCC   │ 3.3V                                 │
 * │ Capacitive Soil Sensor GND   │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ LDR Module AO                │ GPIO 35 (ADC)                        │
 * │ LDR Module VCC               │ 3.3V                                 │
 * │ LDR Module GND               │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ Rain Sensor DO               │ GPIO 27 (LOW = rain, HIGH = dry)     │
 * │ Rain Sensor AO               │ GPIO 33 (ADC)                        │
 * │ Rain Sensor VCC              │ 3.3V                                 │
 * │ Rain Sensor GND              │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ MQ-135 AO                    │ GPIO 32 via voltage divider           │
 * │ MQ-135 VCC                   │ 5V                                   │
 * │ MQ-135 GND                   │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ BMP280 SDA                   │ GPIO 21                              │
 * │ BMP280 SCL                   │ GPIO 22                              │
 * │ BMP280 VCC                   │ 3.3V                                 │
 * │ BMP280 GND                   │ GND                                  │
 * ├──────────────────────────────┼──────────────────────────────────────┤
 * │ OLED SSD1306 SDA             │ GPIO 21                              │
 * │ OLED SSD1306 SCL             │ GPIO 22                              │
 * │ OLED VCC                     │ 3.3V                                 │
 * │ OLED GND                     │ GND                                  │
 * └──────────────────────────────┴──────────────────────────────────────┘
 *
 * MQ-135 Voltage Divider:
 *
 *   MQ-135 AO ── 10kΩ ──┬── GPIO 32
 *                        │
 *                       20kΩ
 *                        │
 *                       GND
 *
 * Required Libraries (install via Arduino IDE → Library Manager):
 *   • DHT sensor library by Adafruit
 *   • Adafruit Unified Sensor
 *   • Adafruit BMP280 Library
 *   • Adafruit SSD1306
 *   • Adafruit GFX Library
 *
 * ────────────────────────────────────────────────────────────────
 */

#include <Wire.h>
#include <DHT.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==================== PIN DEFINITIONS ====================

#define DHT_PIN       4
#define DHT_TYPE      DHT22

#define RAIN_DO_PIN   27

#define MQ135_PIN     32
#define RAIN_AO_PIN   33
#define SOIL_PIN      34
#define LDR_PIN       35

#define I2C_SDA       21
#define I2C_SCL       22

// ==================== OLED ====================

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  OLED_RESET
);

// ==================== SENSOR OBJECTS ====================

DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_BMP280 bmp;

// ==================== SETTINGS ====================

const unsigned long READ_INTERVAL_MS = 2000;
const unsigned long MQ135_WARMUP_MS = 60000;

unsigned long lastReadTime = 0;
unsigned long startTime = 0;

bool bmpAvailable = false;
bool oledAvailable = false;

// ==================== ANALOG AVERAGING ====================

int readAnalogAverage(int pin, int samples = 10) {
  long total = 0;

  for (int i = 0; i < samples; i++) {
    total += analogRead(pin);
    delay(5);
  }

  return total / samples;
}

// ==================== SOIL MOISTURE ====================

int soilPercentage(int rawValue) {
  const int SOIL_DRY_VALUE = 3000;
  const int SOIL_WET_VALUE = 1400;

  int percentage = map(
    rawValue,
    SOIL_DRY_VALUE,
    SOIL_WET_VALUE,
    0,
    100
  );

  return constrain(percentage, 0, 100);
}

// ==================== LDR ====================

int ldrPercentage(int rawValue) {
  int percentage = map(rawValue, 0, 4095, 0, 100);
  return constrain(percentage, 0, 100);
}

// ==================== RAIN INTENSITY ====================

int rainIntensityPercentage(int rawValue) {
  int percentage = map(rawValue, 4095, 0, 0, 100);
  return constrain(percentage, 0, 100);
}

// ==================== MQ135 ====================

int mq135ToAQI(int rawValue) {
  int aqi = map(rawValue, 0, 4095, 200, 3000);
  return constrain(aqi, 200, 3000);
}

// ==================== OLED UPDATE ====================

void updateOLED(
  float temp,
  float hum,
  int soil,
  int light,
  int rainIntensity,
  int rainDetected,
  int aqi,
  float pressure
) {
  if (!oledAvailable) return;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.print("T:");
  display.print(temp, 1);
  display.print("C H:");
  display.print(hum, 0);
  display.println("%");

  display.print("Soil: ");
  display.print(soil);
  display.println("%");

  display.print("Light: ");
  display.print(light);
  display.println("%");

  display.print("Rain: ");
  display.print(rainDetected ? "YES " : "NO  ");
  display.print(rainIntensity);
  display.println("%");

  display.print("AQI: ");
  display.println(aqi);

  display.print("P:");
  display.print(pressure, 1);
  display.println(" hPa");

  display.display();
}

// ==================== SETUP ====================

void setup() {
  Serial.begin(9600);
  delay(1000);

  analogReadResolution(12);

  Wire.begin(I2C_SDA, I2C_SCL);

  dht.begin();

  pinMode(RAIN_DO_PIN, INPUT);

  // BMP280
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    bmpAvailable = true;

    bmp.setSampling(
      Adafruit_BMP280::MODE_NORMAL,
      Adafruit_BMP280::SAMPLING_X2,
      Adafruit_BMP280::SAMPLING_X16,
      Adafruit_BMP280::FILTER_X16,
      Adafruit_BMP280::STANDBY_MS_500
    );
  }

  // OLED
  if (display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    oledAvailable = true;

    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 15);
    display.println("AI Plant Monitor");
    display.println();
    display.println("ESP32 Starting...");
    display.display();
  }

  startTime = millis();
}

// ==================== LOOP ====================

void loop() {

  if (millis() - lastReadTime < READ_INTERVAL_MS) {
    return;
  }

  lastReadTime = millis();

  // DHT22
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    return;
  }

  // ANALOG SENSORS
  int rawSoil = readAnalogAverage(SOIL_PIN);
  int rawLDR = readAnalogAverage(LDR_PIN);
  int rawRain = readAnalogAverage(RAIN_AO_PIN);
  int rawMQ135 = readAnalogAverage(MQ135_PIN);

  // CONVERT VALUES
  int soil = soilPercentage(rawSoil);
  int light = ldrPercentage(rawLDR);
  int rainIntensity = rainIntensityPercentage(rawRain);
  int aqi = mq135ToAQI(rawMQ135);

  // MQ135 WARMUP
  if (millis() - startTime < MQ135_WARMUP_MS) {
    aqi = 450;
  }

  // RAIN DIGITAL OUTPUT
  int rainDetected = (digitalRead(RAIN_DO_PIN) == LOW) ? 1 : 0;

  // PRESSURE
  float pressure = 1013.25;

  if (bmpAvailable) {
    pressure = bmp.readPressure() / 100.0F;
  }

  // OLED
  updateOLED(
    temp,
    hum,
    soil,
    light,
    rainIntensity,
    rainDetected,
    aqi,
    pressure
  );

  // ==================================================
  // EXACT CSV FORMAT REQUIRED BY LUNA AI:
  // TEMP,HUM,AQI,RAIN,PRESSURE
  // ==================================================

  Serial.print(temp, 2);
  Serial.print(",");
  Serial.print(hum, 2);
  Serial.print(",");
  Serial.print(aqi);
  Serial.print(",");
  Serial.print(rainDetected);
  Serial.print(",");
  Serial.print(pressure, 2);
  Serial.println();
}
```
