#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <queue>

const char* ssid = "Redmi Note 11T 5G";
const char* password = "99aAbB*#";
const char* serverName = "http://192.168.28.172:8000/api/ecg/";

#define ECG_PIN 34
#define LEADS_OFF_PLUS 25
#define LEADS_OFF_MINUS 26

const int MAX_BUFFER_SIZE = 500;
const int SEND_INTERVAL = 10000;  // 10 seconds

struct ECGReading {
  float ecgValue;
  unsigned long timestamp;
};

std::queue<ECGReading> ecgBuffer;
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  
  pinMode(ECG_PIN, INPUT);
  pinMode(LEADS_OFF_PLUS, INPUT);
  pinMode(LEADS_OFF_MINUS, INPUT);

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  analogSetWidth(12);

  connectToWiFi();
}

void connectToWiFi() {
  WiFi.disconnect(true);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.println("Connecting to WiFi...");
  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");

    if (millis() - startAttemptTime > 10000) {
      Serial.println("\nFailed to connect to WiFi.");
      WiFi.reconnect();
      return;
    }
  }
  
  Serial.println("\nWiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

float readECGSensor() {
  if ((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
    Serial.println("Lead-off detected!");
    return -1;
  }

  float sum = 0;
  for (int i = 0; i < 4; i++) {
    sum += analogRead(ECG_PIN);
    delayMicroseconds(100);
  }
  
  return sum / 4;
}

void bufferECGReading() {
  float rawValue = readECGSensor();
  
  if (rawValue != -1) {
    ECGReading reading = {
      rawValue,
      millis()
    };
    
    if (ecgBuffer.size() >= MAX_BUFFER_SIZE) {
      ecgBuffer.pop();
    }
    ecgBuffer.push(reading);
  }
}

void sendECGDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
    return;
  }

  if (ecgBuffer.empty()) {
    return;
  }

  HTTPClient http;
  if (!http.begin(serverName)) {
    Serial.println("HTTP connection failed");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  
  // Create JSON with fixed memory
  StaticJsonDocument<6144> doc;  // Increased buffer size
  doc["patient"] = 1;  // Hardcoded patient ID
  JsonArray ecgReadings = doc.createNestedArray("ecg_readings");

  // Limit batch size to prevent memory issues
  int batchSize = min((int)ecgBuffer.size(), 100);
  
  for (int i = 0; i < batchSize; i++) {
    ECGReading reading = ecgBuffer.front();
    ecgBuffer.pop();

    JsonObject jsonReading = ecgReadings.createNestedObject();
    jsonReading["ecg_data"] = reading.ecgValue;
    jsonReading["timestamp"] = reading.timestamp;
  }

  String jsonData;
  serializeJson(doc, jsonData);

  int httpResponseCode = http.POST(jsonData);
  
  Serial.print("HTTP Response Code: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {
    Serial.println("Data sent successfully");
  } else {
    Serial.println("Error sending data");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();


void loop() {
  bufferECGReading();

  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    sendECGDataToServer();
    lastSendTime = currentTime;
  }

  delay(5);
}











// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>
// #include <queue>

// // WiFi Credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server Configuration - DOUBLE CHECK THIS IP
// const char* serverName = "http://192.168.21.172:8000/api/ecg/";

// // ECG and Sampling Configuration
// #define ECG_PIN 34
// #define LEADS_OFF_PLUS 25
// #define LEADS_OFF_MINUS 26

// // Data Buffering Configuration
// const int MAX_BUFFER_SIZE = 500;
// const int SEND_INTERVAL = 10000;  // 10 seconds

// // Data Structures for Buffering
// struct ECGReading {
//   float ecgValue;
//   unsigned long timestamp;
// };

// // Global Variables
// std::queue<ECGReading> ecgBuffer;
// unsigned long lastSendTime = 0;

// void setup() {
//   Serial.begin(115200);
  
//   // Networking Diagnostics Early
//   networkDiagnostics();
  
//   // Configure Pins
//   pinMode(ECG_PIN, INPUT);
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);

//   // ADC Configuration
//   analogReadResolution(12);
//   analogSetAttenuation(ADC_11db);
//   analogSetWidth(12);

//   // Connect to WiFi
//   connectToWiFi();
// }

// void networkDiagnostics() {
//   Serial.println("\n--- Network Diagnostics ---");
//   Serial.print("Attempting to connect to SSID: ");
//   Serial.println(ssid);
//   Serial.print("Password Length: ");
//   Serial.println(strlen(password));
// }

// void connectToWiFi() {
//   WiFi.disconnect(true);  // Disconnect any previous connection
//   delay(1000);

//   WiFi.mode(WIFI_STA);  // Station mode
//   WiFi.begin(ssid, password);

//   Serial.println("\nConnecting to WiFi...");
//   unsigned long startAttemptTime = millis();

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");

//     // 10-second timeout
//     if (millis() - startAttemptTime > 10000) {
//       Serial.println("\nFailed to connect to WiFi.");
//       WiFi.reconnect();
//       return;
//     }
//   }
  
//   Serial.println("\nWiFi Connected!");
//   Serial.print("IP Address: ");
//   Serial.println(WiFi.localIP());
//   Serial.print("Gateway: ");
//   Serial.println(WiFi.gatewayIP());
//   Serial.print("DNS: ");
//   Serial.println(WiFi.dnsIP());
// }

// float readECGSensor() {
//   // Lead-off detection
//   if ((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//     Serial.println("Lead-off detected!");
//     return -1;
//   }

//   // Multiple readings average
//   float sum = 0;
//   for (int i = 0; i < 4; i++) {
//     sum += analogRead(ECG_PIN);
//     delayMicroseconds(100);
//   }
  
//   return sum / 4;
// }

// void bufferECGReading() {
//   float rawValue = readECGSensor();
  
//   if (rawValue != -1) {
//     ECGReading reading = {
//       rawValue,
//       millis()
//     };
    
//     // Buffer management
//     if (ecgBuffer.size() >= MAX_BUFFER_SIZE) {
//       ecgBuffer.pop();
//     }
//     ecgBuffer.push(reading);
//   }
// }

// void sendECGDataToServer() {
//   // Extensive Connection Checks
//   if (WiFi.status() != WL_CONNECTED) {
//     Serial.println("WiFi Disconnected!");
//     connectToWiFi();
//     return;
//   }

//   if (ecgBuffer.empty()) {
//     Serial.println("No data to send");
//     return;
//   }

//   // Network and HTTP Debugging
//   Serial.println("\n--- Sending Data ---");
//   Serial.print("Server URL: ");
//   Serial.println(serverName);
//   Serial.print("WiFi Signal Strength: ");
//   Serial.println(WiFi.RSSI());

//   HTTPClient http;
  
//   // Verify HTTP Connection
//   if (!http.begin(serverName)) {
//     Serial.println("Failed to initialize HTTP connection");
//     return;
//   }

//   http.addHeader("Content-Type", "application/json");
  
//   // JSON Preparation
//   DynamicJsonDocument doc(4096);
//   doc["patient"] = 1;  // REPLACE WITH ACTUAL PATIENT ID
//   JsonArray ecgReadings = doc.createNestedArray("ecg_readings");

//   // Buffer to JSON
//   while (!ecgBuffer.empty()) {
//     ECGReading reading = ecgBuffer.front();
//     ecgBuffer.pop();

//     JsonObject jsonReading = ecgReadings.createNestedObject();
//     jsonReading["ecg_data"] = reading.ecgValue;
//     jsonReading["timestamp"] = reading.timestamp;
//   }

//   // JSON Serialization
//   String jsonData;
//   serializeJsonPretty(doc, Serial);  // Print to Serial for debug
//   serializeJson(doc, jsonData);

//   // Attempt to Send
//   int httpResponseCode = http.POST(jsonData);
  
//   Serial.print("HTTP Response Code: ");
//   Serial.println(httpResponseCode);

//   if (httpResponseCode > 0) {
//     String response = http.getString();
//     Serial.println("Data sent successfully");
//     Serial.println(response);
//   } else {
//     Serial.println("Error sending data");
//     Serial.print("HTTP Error: ");
//     Serial.println(http.errorToString(httpResponseCode));
//   }

//   http.end();
// }

// void loop() {
//   bufferECGReading();

//   unsigned long currentTime = millis();
//   if (currentTime - lastSendTime >= SEND_INTERVAL) {
//     sendECGDataToServer();
//     lastSendTime = currentTime;
//   }

//   delay(5);
// }










// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>
// #include <queue>
// #include <time.h>

// // WiFi Credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server Configuration
// const char* serverName = "http://192.168.1.100:8000/api/ecg/";

// // ECG and Sampling Configuration
// #define ECG_PIN 34
// #define LEADS_OFF_PLUS 25
// #define LEADS_OFF_MINUS 26

// // Data Buffering Configuration
// const int MAX_BUFFER_SIZE = 500;  // Adjust based on available memory
// const int SEND_INTERVAL = 10000;  // 10 seconds between data sends

// // Data Structures for Buffering
// struct ECGReading {
//   float ecgValue;
//   unsigned long timestamp;  // Milliseconds since device start
// };

// // Global Variables
// std::queue<ECGReading> ecgBuffer;
// unsigned long lastSendTime = 0;

// void setup() {
//   Serial.begin(115200);

//   // Configure ECG Pin and Lead-Off Detection
//   pinMode(ECG_PIN, INPUT);
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);

//   // Configure ADC
//   analogReadResolution(12);
//   analogSetAttenuation(ADC_11db);
//   analogSetWidth(12);

//   // Connect to WiFi
//   connectToWiFi();
// }

// // Modify WiFi connection method
// void connectToWiFi() {
//   WiFi.disconnect(true);  // Disconnect first
//   delay(1000);

//   Serial.println("Connecting to WiFi...");
//   WiFi.mode(WIFI_STA);  // Explicitly set to Station mode
//   WiFi.begin(ssid, password);

//   unsigned long startAttemptTime = millis();

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");

//     // Timeout after 10 seconds
//     if (millis() - startAttemptTime > 10000) {
//       Serial.println("\nFailed to connect to WiFi. Restarting...");
//       ESP.restart();
//     }
//   }
  
//   Serial.println("\nConnected to WiFi");
//   Serial.print("IP Address: ");
//   Serial.println(WiFi.localIP());
//   Serial.print("Gateway: ");
//   Serial.println(WiFi.gatewayIP());
//   Serial.print("Subnet Mask: ");
//   Serial.println(WiFi.subnetMask());
// }

// float readECGSensor() {
//   // Check for lead-off condition
//   if ((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//     Serial.println("Lead-off detected!");
//     return -1; // Indicate invalid reading
//   }

//   // Take multiple readings and average
//   float sum = 0;
//   for (int i = 0; i < 4; i++) {
//     sum += analogRead(ECG_PIN);
//     delayMicroseconds(100);
//   }
  
//   return sum / 4;
// }

// void bufferECGReading() {
//   float rawValue = readECGSensor();
  
//   if (rawValue != -1) {
//     ECGReading reading = {
//       rawValue,
//       millis()  // Timestamp in milliseconds since device start
//     };
    
//     // Add to buffer, remove oldest if full
//     if (ecgBuffer.size() >= MAX_BUFFER_SIZE) {
//       ecgBuffer.pop();
//     }
//     ecgBuffer.push(reading);
//   }
// }

// void sendECGDataToServer() {
//   // Check WiFi connection first
//   if (WiFi.status() != WL_CONNECTED) {
//     Serial.println("WiFi Disconnected. Attempting to reconnect...");
//     connectToWiFi();
//     return;
//   }

//   // Additional network diagnostics
//   Serial.print("WiFi Signal Strength (RSSI): ");
//   Serial.println(WiFi.RSSI());

//   if (ecgBuffer.empty()) {
//     Serial.println("No data to send");
//     return;
//   }

//   // More detailed error handling
//   HTTPClient http;
  
//   // Verify server URL
//   Serial.print("Attempting to connect to: ");
//   Serial.println(serverName);

//   // Important: Use begin with full URL
//   if (!http.begin(serverName)) {
//     Serial.println("Failed to initialize HTTP connection");
//     return;
//   }

//   http.addHeader("Content-Type", "application/json");
  
//   // Create JSON document
//   DynamicJsonDocument doc(4096);
  
//   // Patient ID - REPLACE WITH ACTUAL PATIENT ID
//   doc["patient"] = 1;
//   JsonArray ecgReadings = doc.createNestedArray("ecg_readings");

//   // Transfer buffer data to JSON
//   while (!ecgBuffer.empty()) {
//     ECGReading reading = ecgBuffer.front();
//     ecgBuffer.pop();

//     JsonObject jsonReading = ecgReadings.createNestedObject();
//     jsonReading["ecg_data"] = reading.ecgValue;
//     jsonReading["timestamp"] = reading.timestamp;
//   }

//   // Serialize JSON
//   String jsonData;
//   serializeJsonPretty(doc, Serial);  // Print to Serial for debugging
//   serializeJson(doc, jsonData);

//   // More verbose error handling
//   int httpResponseCode;
  
//   try {
//     httpResponseCode = http.POST(jsonData);
    
//     Serial.print("HTTP Response Code: ");
//     Serial.println(httpResponseCode);

//     if (httpResponseCode > 0) {
//       String response = http.getString();
//       Serial.println("Data sent successfully");
//       Serial.println(response);
//     } else {
//       Serial.println("Error sending data");
      
//       // Detailed error logging
//       Serial.print("HTTP Error: ");
//       Serial.println(http.errorToString(httpResponseCode));
//     }
//   } catch (std::exception& e) {
//     Serial.print("Exception in HTTP request: ");
//     Serial.println(e.what());
//   }

//   http.end();
// }



// void loop() {
//   // Continuously buffer ECG readings
//   bufferECGReading();

//   // Check if it's time to send data
//   unsigned long currentTime = millis();
//   if (currentTime - lastSendTime >= SEND_INTERVAL) {
//     sendECGDataToServer();
//     lastSendTime = currentTime;
//   }

//   delay(5);  // Small delay to control sampling rate
// }









// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>

// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server URL
// const char* serverName = "http://192.168.1.100:8000/api/ecg/";

// // ECG parameters
// #define ECG_PIN 34
// #define SAMPLE_RATE 200
// #define DURATION 10
// #define TOTAL_SAMPLES SAMPLE_RATE * DURATION

// // Data storage
// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];
// int currentIndex = 0;

// void setup() {
//   Serial.begin(115200);
  
//   // Connect to WiFi
//   Serial.println("Connecting to WiFi...");
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi");
// }

// void collectECGData() {
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     ecgData[i] = analogRead(ECG_PIN);
//     timestamps[i] = millis();
//     delay(1000 / SAMPLE_RATE);
//   }
// }

// void sendDataToServer() {
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");

//     DynamicJsonDocument doc(2048);
//     doc["patient"] = 1;

//     JsonArray ecgReadings = doc.createNestedArray("ecg_readings");
//     for (int i = 0; i < TOTAL_SAMPLES; i++) {
//       JsonObject reading = ecgReadings.createNestedObject();
//       reading["ecg_data"] = ecgData[i];
//       reading["timestamp"] = timestamps[i];
//     }

//     String jsonData;
//     serializeJson(doc, jsonData);

//     int httpResponseCode = http.POST(jsonData);
//     if (httpResponseCode > 0) {
//       Serial.println("Data sent successfully");
//       Serial.println(http.getString());
//     } else {
//       Serial.println("Error sending data");
//     }
//     http.end();
//   } else {
//     Serial.println("WiFi disconnected");
//   }
// }

// void loop() {
//   collectECGData();
//   currentIndex += TOTAL_SAMPLES;
  
//   if (currentIndex >= TOTAL_SAMPLES * 10) { // Send data every 10 seconds
//     sendDataToServer();
//     currentIndex = 0;
//   }
  
//   delay(1000 / SAMPLE_RATE);
// }














// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>

// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server URL
// const char* serverName = "http://192.168.1.100:8000/api/ecg/";

// // ECG parameters
// #define ECG_PIN 34
// #define SAMPLE_RATE 200
// #define DURATION 10
// #define TOTAL_SAMPLES SAMPLE_RATE * DURATION

// // Data storage
// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];

// void setup() {
//   Serial.begin(115200);
  
//   // Connect to WiFi
//   Serial.println("Connecting to WiFi...");
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi");
// }

// void collectECGData() {
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     ecgData[i] = analogRead(ECG_PIN);
//     timestamps[i] = millis();
//     delay(1000 / SAMPLE_RATE);
//   }
// }

// void sendDataToServer() {
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");

//     DynamicJsonDocument doc(2048);
//     doc["patient"] = 1;

//     JsonArray ecgReadings = doc.createNestedArray("ecg_readings");
//     for (int i = 0; i < TOTAL_SAMPLES; i++) {
//       JsonObject reading = ecgReadings.createNestedObject();
//       reading["ecg_data"] = ecgData[i];
//       reading["timestamp"] = timestamps[i];
//     }

//     String jsonData;
//     serializeJson(doc, jsonData);

//     int httpResponseCode = http.POST(jsonData);
//     if (httpResponseCode > 0) {
//       Serial.println("Data sent successfully");
//       Serial.println(http.getString());
//     } else {
//       Serial.println("Error sending data");
//     }
//     http.end();
//   } else {
//     Serial.println("WiFi disconnected");
//   }
// }

// void loop() {
//   collectECGData();
//   sendDataToServer();
//   delay(10000);
// }










// #include <WiFi.h>
// #include <HTTPClient.h>
// #include "time.h"

// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server URL
// const char* serverName = "http://192.168.1.100:8000/api/ecg/";

// // ECG parameters
// #define ECG_PIN 34
// #define SAMPLE_RATE 200
// #define DURATION 10
// #define TOTAL_SAMPLES SAMPLE_RATE * DURATION

// // Data storage
// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];

// void setup() {
//   Serial.begin(115200);
  
//   // Connect to WiFi
//   Serial.println("Connecting to WiFi...");
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi");

//   // NTP setup for timestamping
//   configTime(0, 0, "pool.ntp.org");
// }

// void collectECGData() {
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     ecgData[i] = analogRead(ECG_PIN);
//     timestamps[i] = millis();
//     delay(1000 / SAMPLE_RATE);
//   }
// }

// String createJSON() {
//   String json = "{\"patient\":1,\"ecg_readings\":[";
  
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     json += "{\"ecg_data\":" + String(ecgData[i]) + ",\"timestamp\":" + String(timestamps[i]) + "}";
//     if (i < TOTAL_SAMPLES - 1) json += ",";
//   }
  
//   json += "]}";
//   return json;
// }

// void sendDataToServer() {
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");
//     String jsonData = createJSON();
//     int httpResponseCode = http.POST(jsonData);
//     if (httpResponseCode > 0) {
//       Serial.println("Data sent successfully");
//       Serial.println(http.getString());
//     } else {
//       Serial.println("Error sending data");
//     }
//     http.end();
//   } else {
//     Serial.println("WiFi disconnected");
//   }
// }

// void loop() {
//   collectECGData();
//   sendDataToServer();
//   delay(10000);
// }


// #include <WiFi.h>
// #include <HTTPClient.h>
// #include "time.h"

// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Server URL
// const char* serverName = "http://192.168.1.100:8000/api/ecg/";

// // ECG parameters
// #define ECG_PIN 34
// #define SAMPLE_RATE 200
// #define DURATION 10
// #define TOTAL_SAMPLES SAMPLE_RATE * DURATION

// // Data storage
// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];

// void setup() {
//   Serial.begin(115200);
  
//   // Connect to WiFi
//   Serial.println("Connecting to WiFi...");
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi");

//   // NTP setup for timestamping
//   configTime(0, 0, "pool.ntp.org");
// }

// void collectECGData() {
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     ecgData[i] = analogRead(ECG_PIN);
//     timestamps[i] = millis();
//     delay(1000 / SAMPLE_RATE);
//   }
// }

// String createJSON() {
//   String json = "{\"patient\":1,\"ecg_readings\":[";
  
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     json += "{\"ecg_data\":" + String(ecgData[i]) + ",\"timestamp\":" + String(timestamps[i]) + "}";
//     if (i < TOTAL_SAMPLES - 1) json += ",";
//   }
  
//   json += "]}";
//   return json;
// }

// void sendDataToServer() {
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");

//     String jsonData = createJSON();
//     int httpResponseCode = http.POST(jsonData);

//     if (httpResponseCode > 0) {
//       Serial.println("Data sent successfully");
//       Serial.println(http.getString());
//     } else {
//       Serial.println("Error sending data");
//     }

//     http.end();
//   } else {
//     Serial.println("WiFi disconnected");
//   }
// }

// void loop() {
//   collectECGData();
//   sendDataToServer();
//   delay(10000);
// }













// #include <WiFi.h>
// #include <HTTPClient.h>
// #include "time.h"

// // Wi-Fi credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Django server URL
// const char* serverName = "http://192.168.111.172:8000/api/ecg/";

// // NTP server settings
// const char* ntpServer = "pool.ntp.org";
// const long gmtOffset_sec = 0;
// const int daylightOffset_sec = 0;

// // ECG parameters
// #define ECG_PIN 34
// #define LEADS_OFF_PLUS 25
// #define LEADS_OFF_MINUS 26

// // Data storage
// const int SAMPLE_RATE = 200;  // 200 Hz
// const int DURATION = 10;      // 10 seconds
// const int TOTAL_SAMPLES = SAMPLE_RATE * DURATION;

// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];

// void setup() {
//   Serial.begin(115200);

//   // Configure ECG input
//   analogReadResolution(12);
//   pinMode(ECG_PIN, INPUT);
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);

//   // Connect to Wi-Fi
//   Serial.println("Connecting to WiFi...");
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi. IP: " + WiFi.localIP());

//   // Initialize NTP for timestamping
//   configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
// }

// String getFormattedTime(unsigned long milliseconds) {
//   struct tm timeinfo;
//   if (!getLocalTime(&timeinfo)) {
//     return "1970-01-01T00:00:00.000Z";
//   }
  
//   char buffer[30];
//   snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03luZ",
//            timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
//            timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec, milliseconds % 1000);
//   return String(buffer);
// }

// void loop() {
//   // Check leads status
//   if (digitalRead(LEADS_OFF_PLUS) == 1 || digitalRead(LEADS_OFF_MINUS) == 1) {
//     Serial.println("Leads off detected!");
//     delay(1000);
//     return;
//   }

//   // Collect ECG data for 10 seconds
//   Serial.println("Collecting ECG data...");
//   for (int i = 0; i < TOTAL_SAMPLES; i++) {
//     ecgData[i] = analogRead(ECG_PIN);
//     timestamps[i] = millis();  // Store timestamp in milliseconds
//     delay(1000 / SAMPLE_RATE); // Maintain sample rate
//   }

//   // Send data to server
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");

//     String jsonData = "{\"patient\":1,\"ecg_readings\":[";
//     for (int i = 0; i < TOTAL_SAMPLES; i++) {
//       jsonData += "{\"ecg_data\":" + String(ecgData[i], 3) + ",\"timestamp\":\"" + getFormattedTime(timestamps[i]) + "\"}";
//       if (i < TOTAL_SAMPLES - 1) jsonData += ",";
//     }
//     jsonData += "]}";

//     int httpResponseCode = http.POST(jsonData);
//     if (httpResponseCode > 0) {
//       Serial.println("Data sent successfully!");
//       Serial.println("Response: " + http.getString());
//     } else {
//       Serial.println("Error sending data. HTTP Response code: " + String(httpResponseCode));
//     }
//     http.end();
//   } else {
//     Serial.println("WiFi disconnected. Reconnecting...");
//   }

//   delay(10000);  // Wait 10 seconds before next loop
// }












// #include <WiFi.h>
// #include <HTTPClient.h>

// // Wi-Fi credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Your Django server address
// const char* serverName = "http://192.168.111.172:8000/api/ecg/";

// // ECG parameters
// #define ECG_PIN 34
// #define LEADS_OFF_PLUS 25
// #define LEADS_OFF_MINUS 26

// // Data storage
// const int SAMPLE_RATE = 200; // 200 Hz
// const int DURATION = 10;     // 10 seconds
// const int TOTAL_SAMPLES = SAMPLE_RATE * DURATION;

// float ecgData[TOTAL_SAMPLES];
// unsigned long timestamps[TOTAL_SAMPLES];

// // Connection and filter variables
// float baseline = 2048;
// int sampleIndex = 0;

// // Function to get formatted time (with milliseconds)
// String getFormattedTime() {
//   struct tm timeinfo;
//   if (!getLocalTime(&timeinfo)) {
//     return "1970-01-01T00:00:00.000Z"; // Default if no time available
//   }
//   char buffer[25];
//   snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ",
//            timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
//            timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec, millis() % 1000);
//   return String(buffer);
// }

// void setup() {
//   Serial.begin(115200);

//   // Configure ECG input
//   analogReadResolution(12);
//   pinMode(ECG_PIN, INPUT);
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);

//   // Connect to Wi-Fi
//   WiFi.begin(ssid, password);
//   Serial.println("Connecting to WiFi...");
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi. IP: " + WiFi.localIP());
// }

// void loop() {
//   if ((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//     Serial.println("Leads off detected!");
//     return;
//   }

//   // Collect data for 10 seconds
//   for (sampleIndex = 0; sampleIndex < TOTAL_SAMPLES; sampleIndex++) {
//     ecgData[sampleIndex] = analogRead(ECG_PIN);
//     timestamps[sampleIndex] = millis(); // Capture timestamp
//     delay(1000 / SAMPLE_RATE);          // Maintain sample rate
//   }

//   // Send data to server
//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(serverName);
//     http.addHeader("Content-Type", "application/json");

//     String jsonData = "{\"patient\":1,\"ecg_readings\":[";
//     for (int i = 0; i < TOTAL_SAMPLES; i++) {
//       jsonData += "{\"ecg_data\":" + String(ecgData[i], 3) + ",\"timestamp\":\"" + getFormattedTime() + "\"}";
//       if (i < TOTAL_SAMPLES - 1) jsonData += ",";
//     }
//     jsonData += "]}";

//     int httpResponseCode = http.POST(jsonData);
//     if (httpResponseCode > 0) {
//       Serial.println("Data sent. Response: " + http.getString());
//     } else {
//       Serial.println("Error sending data: " + String(httpResponseCode));
//     }
//     http.end();
//   } else {
//     Serial.println("WiFi disconnected. Reconnecting...");
//   }

//   delay(10000); // Wait 10 seconds before next loop
// }













// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <NTPClient.h>
// #include <WiFiUdp.h>

// // Wi-Fi credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // NTP server settings
// WiFiUDP ntpUDP;
// NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);  // UTC time, update every 60 seconds

// // Server endpoint
// const char* serverName = "http://192.168.21.172:8000/api/ecg/";

// // Constants
// const int ECG_PIN = 34;
// const int BUFFER_SIZE = 2000; // 10 seconds at 200 Hz
// const int SAMPLE_INTERVAL = 5; // 5 ms for 200 Hz sampling

// // Data storage
// float ecgData[BUFFER_SIZE];
// String timestamps[BUFFER_SIZE];
// int bufferIndex = 0;

// void setup() {
//   Serial.begin(115200);

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("Connected to WiFi");

//   timeClient.begin();
// }

// void loop() {
//   timeClient.update(); // Update time from NTP

//   // Read ECG data
//   float rawValue = analogRead(ECG_PIN);
//   unsigned long msSinceStart = millis() % 1000; // Milliseconds within current second

//   // Format date and time
//   String formattedTime = getFormattedDateTime(msSinceStart);

//   // Store data in buffer
//   if (bufferIndex < BUFFER_SIZE) {
//     ecgData[bufferIndex] = rawValue;
//     timestamps[bufferIndex] = formattedTime;
//     bufferIndex++;
//   } else {
//     // Send data to server once buffer is full
//     sendECGData();
//     bufferIndex = 0;
//   }

//   delay(SAMPLE_INTERVAL); // Maintain 200 Hz sampling rate
// }

// String getFormattedDateTime(unsigned long ms) {
//   time_t epochTime = timeClient.getEpochTime();
//   struct tm* ptm = gmtime(&epochTime);

//   char dateTimeBuffer[25];
//   sprintf(dateTimeBuffer, "%02d/%02d/%04d %02d:%02d:%02d.%03lu", 
//     ptm->tm_mday, ptm->tm_mon + 1, ptm->tm_year + 1900, 
//     ptm->tm_hour, ptm->tm_min, ptm->tm_sec, ms);

//   return String(dateTimeBuffer);
// }

// void sendECGData() {
//   HTTPClient http;
//   http.begin(serverName);
//   http.addHeader("Content-Type", "application/json");

//   // Create JSON payload
//   String jsonData = "{\"data\":[";
//   for (int i = 0; i < BUFFER_SIZE; i++) {
//     jsonData += "{\"timestamp\":\"" + timestamps[i] + "\",\"value\":" + String(ecgData[i]) + "}";
//     if (i < BUFFER_SIZE - 1) jsonData += ",";
//   }
//   jsonData += "]}";

//   // Send POST request
//   int httpResponseCode = http.POST(jsonData);

//   if (httpResponseCode > 0) {
//     Serial.print("HTTP Response code: ");
//     Serial.println(httpResponseCode);
//   } else {
//     Serial.print("Error code: ");
//     Serial.println(httpResponseCode);
//   }

//   http.end(); // Free resources
// }






// #include <OneWire.h>

// #include <WiFi.h>
// #include <HTTPClient.h>

// // Data wire is connected to GPIO 4
// #define ONE_WIRE_BUS 4

// // Wi-Fi credentials
// const char* ssid = "Redmi Note 11T 5G";
// const char* password = "99aAbB*#";

// // Your Django server address (replace with your actual server address)
// const char* serverName = "http://192.168.111.172:8000/api/temperature/";



// // Adjust these constants for better smoothing
// const int SAMPLES = 15;        // Increase from 10 to 15 for smoother signal
// const float ALPHA = 0.15;      // Adjust from 0.1 to 0.15 for better response

// // Add bandpass filter parameters
// const float LOWPASS_CUTOFF = 0.5;    // 0.5 Hz cutoff for low frequencies
// const float HIGHPASS_CUTOFF = 40;    // 40 Hz cutoff for high frequencies

// // Constants for filtering
// const int ECG_PIN = 34;           // ECG signal pin
// const int LEADS_OFF_PLUS = 25;    // LO+ pin
// const int LEADS_OFF_MINUS = 26;   // LO- pin

// // Butterworth filter coefficients
// float b[] = {0.0316, 0.0632, 0.0316};  // Numerator coefficients
// float a[] = {1.0000, -1.4252, 0.5516}; // Denominator coefficients
// float x[3] = {0, 0, 0};  // Input buffer
// float y[3] = {0, 0, 0};  // Output buffer

// void setup() {

//   WiFi.begin(ssid, password);
//   Serial.println("Connecting to WiFi");
//   while(WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("");
//   Serial.print("Connected to WiFi network with IP Address: ");
//   Serial.println(WiFi.localIP());



//   Serial.begin(9600);
  
//   // Configure ADC
//   analogReadResolution(12);
//   analogSetAttenuation(ADC_11db);
//   analogSetWidth(12);
  
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);
//   pinMode(ECG_PIN, INPUT);
// }

// // Butterworth filter implementation
// float butterworthFilter(float newValue) {
//   // Shift the input buffer
//   x[2] = x[1];
//   x[1] = x[0];
//   x[0] = newValue;
  
//   // Shift the output buffer
//   y[2] = y[1];
//   y[1] = y[0];
  
//   // Apply the filter
//   y[0] = b[0]*x[0] + b[1]*x[1] + b[2]*x[2] - a[1]*y[1] - a[2]*y[2];
  
//   return y[0];
// }

// void loop() {

//    // Check WiFi connection status
//   if(WiFi.status() == WL_CONNECTED){

//   if((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//     Serial.println('!');
//   } else {
//     // Take multiple readings
//     float sum = 0;
//     for(int i = 0; i < 4; i++) {
//       sum += analogRead(ECG_PIN);
//       delayMicroseconds(100);
//     }
//     float rawValue = sum / 4;
    
//     // Apply Butterworth filter
//     float filteredValue = butterworthFilter(rawValue);
    
//     // Apply baseline correction
//     static float baseline = 2048;
//     baseline = 0.995 * baseline + 0.005 * filteredValue;
//     filteredValue -= baseline;
    
//     // Map to appropriate range
//     int outputValue = map(filteredValue, -2048, 2048, 0, 4095);
    
//     Serial.println(outputValue);
//   }
  
//   delay(5);  // 200Hz sampling rate
// }