# ⚡ VoltGuard AI: The Surgical Black Box for Grids

**VoltGuard AI** is an Enterprise-Grade Digital Twin and Edge-AI monitoring system designed to protect institutional electrical infrastructure. Developed and validated at **Aravali College of Engineering And Management (ACEM)**, this system goes beyond simple metering to provide predictive diagnostics and "Surgical Load Shedding."

-----

## 🚀 Key Features

  * **Digital Twin Architecture:** A real-time virtual replica of the campus grid that compares live waveforms against "Healthy" benchmarks.
  * **Edge-AI Signature Analysis:** Uses **TinyML (Edge Impulse)** to identify specific appliance "heartbeats" (NILM) directly on the ESP32-S3.
  * **Surgical Load Shedding:** Instead of total blackouts, our AI identifies and cuts only non-essential high-load devices during peak surges.
  * **2FA Command Security:** Critical grid switching requires **Two-Factor Authentication** via a secure Python/Flask backend.
  * **Non-Invasive Retrofit:** Uses **Split-Core CT Sensors** for 15-minute "Live" installation without a power shutdown.

-----

## 🛠️ Technical Stack

### **Hardware (The Edge)**

  * **Microcontroller:** ESP32-S3 (Dual-core, Wi-Fi/BLE)
  * **Sensors:** SCT-013 Current Transformers & ZMPT101B Voltage Sensors
  * **Protocols:** MQTT, ESP-NOW (for offline mesh connectivity), TLS 1.3

### **Software **
* **(The Digital Twin)**
* **BLYNK**

-----

## 🛡️ Security Protocol

VoltGuard AI implements a **Triple-Shield** security model:

1.  **AES-256 Encryption:** All telemetry data is encrypted in transit.
2.  **Air-Gapped Safety:** Local hardware logic overrides cloud commands if they violate pre-set physical safety ceilings.
3.  **OTP Verification:** Manual relay control requires a one-time password sent to the Chief Electrician's registered device.

-----

## 📈 Business & Scalability

VoltGuard operates on a **Hardware + SaaS** model:

  * **Low CapEx:** Standardized hardware components keep deployment costs under ₹2,500 per node.
  * **Multi-Tenancy:** The cloud dashboard is designed to scale to 100+ campuses with zero extra coding effort.
  * **ROI:** Achieve 100% Return on Investment by preventing a single transformer failure (valued at ₹5L+).
    
# Link to wokwi simulation: https://wokwi.com/projects/458994891250981889

<img width="1919" height="831" alt="image" src="https://github.com/user-attachments/assets/5287220b-471d-4c09-ac8d-826c4a181712" />


# Link to digital twin: https://app.snowflake.com/streamlit/sxfcbph/ri61977/#/apps/avw642oi3ekyjbwiag6v

<img width="1771" height="769" alt="image" src="https://github.com/user-attachments/assets/39a2b12c-b8cf-45dc-9eeb-d07720a77773" />

<img width="1798" height="787" alt="image" src="https://github.com/user-attachments/assets/94509eee-3e40-4fa5-a0ae-8c3da7964f4c" />

<img width="1794" height="789" alt="image" src="https://github.com/user-attachments/assets/40a9dcb1-820f-4f13-a913-79b2b2270c3a" />
