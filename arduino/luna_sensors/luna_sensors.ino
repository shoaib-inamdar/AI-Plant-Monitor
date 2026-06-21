/*
 * luna_sensors.ino
 * ────────────────────────────────────────────────────────────────
 * Luna AI Plant Care System — Arduino Sensor Firmware
 * Sends sensor readings as CSV over USB Serial every 2 seconds.
 *
 * CSV Format (one line per reading):
 *   TEMP,HUM,AQI,RAIN,PRESSURE
 *   e.g. 24.30,62.10,450,0,1013.50
 *
 * To use:
 *   1. Upload this sketch to your Arduino
 *   2. In python/config.py set:
 *        SERIAL_PORT = "COM3"   ← your actual port (check Arduino IDE)
 *   3. In main.py set:
 *        reader = SerialReader(use_simulator=False)
 *   That's all — Luna reads the CSV automatically.
 *
 * Wiring Guide:
 * ┌──────────────┬───────────────────────────────────────┐
 * │ Sensor       │ Arduino Pin                           │
 * ├──────────────┼───────────────────────────────────────┤
 * │ DHT22 DATA   │ Digital 2                             │
 * │ DHT22 VCC    │ 5V                                    │
 * │ DHT22 GND    │ GND                                   │
 * ├──────────────┼───────────────────────────────────────┤
 * │ MQ-135 AOUT  │ Analog A0                             │
 * │ MQ-135 VCC   │ 5V                                    │
 * │ MQ-135 GND   │ GND                                   │
 * ├──────────────┼───────────────────────────────────────┤
 * │ Rain DO      │ Digital 4  (HIGH=dry, LOW=rain)       │
 * │ Rain VCC     │ 3.3V                                  │
 * │ Rain GND     │ GND                                   │
 * ├──────────────┼───────────────────────────────────────┤
 * │ BMP280 SDA   │ A4 (Uno) / SDA (Mega/Leonardo)        │
 * │ BMP280 SCL   │ A5 (Uno) / SCL (Mega/Leonardo)        │
 * │ BMP280 VCC   │ 3.3V                                  │
 * │ BMP280 GND   │ GND                                   │
 * └──────────────┴───────────────────────────────────────┘
 *
 * Required Libraries (install via Arduino IDE → Library Manager):
 *   • DHT sensor library by Adafruit   (search "DHT sensor library")
 *   • Adafruit Unified Sensor           (dependency of DHT library)
 *   • Adafruit BMP280 Library           (search "Adafruit BMP280")
 * ────────────────────────────────────────────────────────────────
 */

#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

// ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
#define DHT_PIN       2       // DHT22 data pin
#define DHT_TYPE      DHT22   // DHT22 (also works with DHT11 if you change this)
#define MQ135_PIN     A0      // MQ-135 analog output
#define RAIN_PIN      4       // Rain sensor digital output

// ── CONSTANTS ─────────────────────────────────────────────────────────────────
#define READ_INTERVAL_MS  2000   // Send a reading every 2 seconds
#define MQ135_WARMUP_MS   60000  // MQ-135 needs 60 seconds to warm up

// ── SENSOR OBJECTS ────────────────────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_BMP280 bmp;          // Uses I2C by default

// ── STATE ─────────────────────────────────────────────────────────────────────
bool bmpAvailable  = false;   // Set to true if BMP280 is detected on startup
bool mq135Warmed   = false;   // Set to true after warmup period
unsigned long startTime = 0;

void setup() {
  Serial.begin(9600);

  // DHT22
  dht.begin();

  // Rain sensor pin — read digital value
  pinMode(RAIN_PIN, INPUT);

  // BMP280 — try to initialise; not fatal if absent
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    bmpAvailable = true;
    bmp.setSampling(
      Adafruit_BMP280::MODE_NORMAL,
      Adafruit_BMP280::SAMPLING_X2,
      Adafruit_BMP280::SAMPLING_X16,
      Adafruit_BMP280::FILTER_X16,
      Adafruit_BMP280::STANDBY_MS_500
    );
    Serial.println("# BMP280 detected");
  } else {
    Serial.println("# BMP280 not found — using default pressure 1013.25 hPa");
  }

  // Record startup time for MQ-135 warmup
  startTime = millis();
  Serial.println("# Luna sensor firmware ready. Warming up MQ-135...");
  Serial.println("# CSV format: TEMP,HUM,AQI,RAIN,PRESSURE");
  Serial.println("# RAIN: 0=dry, 1=rain detected");
}

void loop() {
  // ── Read DHT22 ──────────────────────────────────────────────────────────────
  float temp = dht.readTemperature();   // Celsius
  float hum  = dht.readHumidity();      // %

  // Check for DHT22 read failure
  if (isnan(temp) || isnan(hum)) {
    Serial.println("# ERROR: DHT22 read failed. Check wiring.");
    delay(READ_INTERVAL_MS);
    return;
  }

  // ── Read MQ-135 ─────────────────────────────────────────────────────────────
  // MQ-135 needs 60 seconds to warm up for accurate readings.
  // During warmup, we still send data but mark it as approximate.
  int rawAQI = analogRead(MQ135_PIN);   // 0–1023

  // Convert raw 10-bit reading to approximate ppm.
  // This is a simplified linear mapping — real MQ-135 calibration needs
  // reference gas (clean air baseline). For a plant monitor, relative
  // changes matter more than absolute ppm values.
  int aqi = map(rawAQI, 0, 1023, 200, 3000);

  if (millis() - startTime < MQ135_WARMUP_MS) {
    // During warmup, cap at a safe default to avoid false alerts in Luna
    aqi = 450;
  }

  // ── Read Rain Sensor ────────────────────────────────────────────────────────
  // Rain module: DO is LOW when rain detected, HIGH when dry
  // We invert it so Luna gets: 1=rain, 0=dry (matches existing logic)
  int rain = (digitalRead(RAIN_PIN) == LOW) ? 1 : 0;

  // ── Read BMP280 ─────────────────────────────────────────────────────────────
  float pressure = 1013.25;   // fallback if BMP280 not present
  if (bmpAvailable) {
    pressure = bmp.readPressure() / 100.0F;  // Pa → hPa
  }

  // ── Send CSV Line ───────────────────────────────────────────────────────────
  // Format: TEMP,HUM,AQI,RAIN,PRESSURE
  // Python SerialReader.parse_line() expects exactly this format.
  Serial.print(temp,    2);   Serial.print(",");
  Serial.print(hum,     2);   Serial.print(",");
  Serial.print(aqi);          Serial.print(",");
  Serial.print(rain);         Serial.print(",");
  Serial.print(pressure, 2);  Serial.println();   // \n terminates the line

  delay(READ_INTERVAL_MS);
}
