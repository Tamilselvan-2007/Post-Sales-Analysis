#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define LCD_ADDR 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

const int ADC_PIN = 35;        // ADC pin for voltage
const int SWITCH_PIN = 15;     // Switch to GND

LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);
float latestVoltage = 0;

// Wi-Fi credentials
const char* ssid = "Redmi 12 5G";
const char* password = "1234XXXX";

// Flask server endpoint
const char* serverUrl = "http://10.80.229.35:5000/detect/esp_voltage";
const char* checkResumeUrl = "http://10.80.229.35:5000/detect/check_resume";

// Point list in sequence (matches your voltage table)
const char* POINTS[] = {
  "A1","A2","A3","A4","A5","A6","A7","A8","A9",
  "B1","B2","B3","B4","B5","B6","B7","B8","B9",
  "C1","C2",
  "D1","D2","D3",
  "E1","E2",
  "F1","F2","F3","F4","F5",
  "G1","G2","G3","G4","G5","G6",
  "H1","H2",
  "I1","I2",
  "J1","J2",
  "K1","K2",
  "L1","L2","L3",
  "M1","M2","M3",
  "N1","N2","N3",
  "O1","O2",
  "P1","P2",
  "Q1","Q2",
  "R1","R2",
  "S1","S2",
  "T1","T2",
  "U1","U2","U3",
  "V1","V2",
  "W1","W2",
  "X1","X2",
  "Y1","Y2",
  "Z1","Z2",
  "RF"
};
const int TOTAL_POINTS = sizeof(POINTS) / sizeof(POINTS[0]);

int currentIndex = 0;  // tracks A1 → A2 → …
bool isRunning = false; // Automatic loop state

// ---------------------------
// WIFI CONNECT FUNCTION
// ---------------------------
void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  lcd.clear();
  lcd.print("Connecting WiFi");
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  lcd.clear();
  if (WiFi.status() == WL_CONNECTED) {
    lcd.print("WiFi Connected");
    Serial.println("WiFi Connected");
  } else {
    lcd.print("WiFi Failed");
    Serial.println("WiFi Connection Failed");
  }
  delay(800);
  lcd.clear();
}

// ---------------------------
// WAIT FOR RESUME FUNCTION
// ---------------------------
void waitForResume() {
  lcd.setCursor(0, 1);
  lcd.print("Paused...       "); // Update LCD
  
  while (true) {
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(checkResumeUrl);
      int httpCode = http.GET();
      
      if (httpCode > 0) {
        String payload = http.getString();
        StaticJsonDocument<200> doc;
        deserializeJson(doc, payload);
        const char* cmd = doc["command"];
        
        if (String(cmd) == "RESUME") {
          Serial.println("Resume signal received!");
          lcd.setCursor(0, 1);
          lcd.print("Resuming...     ");
          http.end();
          break; // Exit pause loop
        }
      }
      http.end();
    }
    delay(1000); // Poll every second
  }
}

// ---------------------------
// SEND DATA FUNCTION
// ---------------------------
String sendVoltageToServer(const char* point, float value) {
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["point"] = point;
  doc["value"] = value;

  String jsonBody;
  serializeJson(doc, jsonBody);

  Serial.print("Sending JSON: ");
  Serial.println(jsonBody);

  String response = "CONTINUE";
  int httpResponseCode = http.POST(jsonBody);
  
  if (httpResponseCode > 0) {
    String payload = http.getString();
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    Serial.println(payload);
    
    // Parse response for command
    StaticJsonDocument<200> respDoc;
    deserializeJson(respDoc, payload);
    const char* cmd = respDoc["command"];
    if (cmd) response = String(cmd);
    
  } else {
    Serial.print("Error on sending POST: ");
    Serial.println(httpResponseCode);
  }

  http.end();
  return response;
}

void setup() {
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();

  Serial.begin(115200);

  pinMode(SWITCH_PIN, INPUT_PULLUP);
  analogReadResolution(12);
  analogSetPinAttenuation(ADC_PIN, ADC_11db);

  lcd.print("Voltage Meter");
  delay(1200);
  lcd.clear();

  connectWiFi();
}

void loop() {
  // Ensure WiFi is alive
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  // 1. Check for Technician Trigger (Start Sequence)
  if (!isRunning) {
    lcd.setCursor(0, 0);
    lcd.print("Ready to Start  ");
    
    if (digitalRead(SWITCH_PIN) == LOW) {
      Serial.println("Technician Triggered Sequence");
      lcd.clear();
      lcd.print("Starting...");
      isRunning = true;
      currentIndex = 0;
      delay(500); // Debounce
    }
  }

  // 2. Automatic Sequential Loop
  if (isRunning) {
    if (currentIndex < TOTAL_POINTS) {
      const char* currentPoint = POINTS[currentIndex];
      
      // Read voltage
      long total = 0;
      const int samples = 20;
      for (int i = 0; i < samples; i++) {
        total += analogRead(ADC_PIN);
        delay(3);
      }
      float raw = total / (float)samples;
      latestVoltage = raw * (3.300 / 4095.0);

      // Update LCD
      lcd.setCursor(0,0);
      lcd.print("Pt:");
      lcd.print(currentPoint);
      lcd.print(" V:");
      lcd.print(latestVoltage, 2);
      lcd.print("   ");

      // Send to Flask
      String status = sendVoltageToServer(currentPoint, latestVoltage);

      // 3. Pause Logic
      if (status == "PAUSE") {
        Serial.println("Status NOT OK. Pausing loop at SAME point...");
        waitForResume();
        // After resume, we do NOT increment currentIndex.
        // The loop will repeat, re-reading and re-sending the SAME point.
        Serial.println("Resuming... Re-measuring same point.");
      } else {
        // Status is CONTINUE (OK)
        // Move to next point
        currentIndex++;
        delay(500); // Small delay between points
      }
    } else {
      Serial.println("Sequence Completed");
      lcd.clear();
      lcd.print("Done!");
      isRunning = false;
      delay(2000);
    }
  }
}

