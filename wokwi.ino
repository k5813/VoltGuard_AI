#define BLYNK_TEMPLATE_ID "TMPL3KAGNQUuw"
#define BLYNK_TEMPLATE_NAME "VOLTGUARD AI"
#define BLYNK_AUTH_TOKEN "FCSwhD82fvXRs34E-3xfnbrjzuIC2WmU"

#define BLYNK_PRINT Serial
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

// Wokwi WiFi Credentials (standard for Wokwi simulation)
char ssid[] = "Wokwi-GUEST";
char pass[] = "";

// Pin Definitions
const int sensorPin = 4;   // Potentiometer linked to GPIO 4 (ADC1)
const int relayPin = 5;    // Relay Control linked to GPIO 5
const int threshold = 2200; // Surge limit in Watts

BlynkTimer timer;
bool isSurgeActive = false; // Prevents notification spam

// --- Function to Send Data to Blynk & React Dashboard ---
void monitorSystem() {
  int rawValue = analogRead(sensorPin);
  
  // Mapping 12-bit ADC (0-4095) to 0-3000 Watts
  float watts = map(rawValue, 0, 4095, 0, 3000);

  // 1. Update Blynk Mobile Graph (V1)
  Blynk.virtualWrite(V1, watts);

  // 2. Update React Dashboard (Via Serial Monitor Bridge)
  Serial.print("DLive Power:");
  Serial.print(watts);
  Serial.println("W");

  // 3. Safety & Notification Logic
  if (watts > threshold) {
    digitalWrite(relayPin, LOW); // CRITICAL: Trip Relay (Off)
    Blynk.virtualWrite(V2, 1);    // Trigger the Alarm Widget on Dashboard
    
    // Trigger mobile notification only once per surge event
    if (!isSurgeActive) {
      Blynk.logEvent("surge_detected", String("Critical Surge: ") + watts + "W");
      isSurgeActive = true;
    }
  } else {
    // Normal Operation
    digitalWrite(relayPin, HIGH); // System Nominal (On)
    Blynk.virtualWrite(V2, 0);    // Stop the Alarm Widget
    isSurgeActive = false;        // Reset notification flag
  }
}

// --- Remote Manual Control from Blynk App (V2 Switch) ---
BLYNK_WRITE(V2) {
  int state = param.asInt();
  // Ensure we don't turn it back on manually if the surge is still active
  if (!isSurgeActive) {
    digitalWrite(relayPin, state);
    Serial.println(state ? "SYSTEM: Manual Power ON" : "SYSTEM: Manual Power OFF");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Default to ON

  // Connect to Blynk Cloud via Wokwi WiFi Gateway
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Set monitoring frequency (Every 500ms for a "Live" feel)
  timer.setInterval(500L, monitorSystem);
  
  Serial.println("------------------------------------");
  Serial.println("VOLTGUARD AI: SYSTEM ONLINE");
  Serial.println("S3 CORE CONNECTED TO CLOUD");
  Serial.println("------------------------------------");
}

void loop() {
  Blynk.run();
  timer.run();
}
