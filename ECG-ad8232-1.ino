// Adjust these constants for better smoothing
const int SAMPLES = 15;        // Increase from 10 to 15 for smoother signal
const float ALPHA = 0.15;      // Adjust from 0.1 to 0.15 for better response

// Add bandpass filter parameters
const float LOWPASS_CUTOFF = 0.5;    // 0.5 Hz cutoff for low frequencies
const float HIGHPASS_CUTOFF = 40;    // 40 Hz cutoff for high frequencies

// Constants for filtering
const int ECG_PIN = 34;           // ECG signal pin
const int LEADS_OFF_PLUS = 25;    // LO+ pin
const int LEADS_OFF_MINUS = 26;   // LO- pin

// Butterworth filter coefficients
float b[] = {0.0316, 0.0632, 0.0316};  // Numerator coefficients
float a[] = {1.0000, -1.4252, 0.5516}; // Denominator coefficients
float x[3] = {0, 0, 0};  // Input buffer
float y[3] = {0, 0, 0};  // Output buffer

void setup() {
  Serial.begin(9600);
  
  // Configure ADC
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  analogSetWidth(12);
  pinMode(LEADS_OFF_PLUS, INPUT);
  pinMode(LEADS_OFF_MINUS, INPUT);
  pinMode(ECG_PIN, INPUT);
}

// Butterworth filter implementation
float butterworthFilter(float newValue) {
  // Shift the input buffer
  x[2] = x[1];
  x[1] = x[0];
  x[0] = newValue;
  
  // Shift the output buffer
  y[2] = y[1];
  y[1] = y[0];
  
  // Apply the filter
  y[0] = b[0]*x[0] + b[1]*x[1] + b[2]*x[2] - a[1]*y[1] - a[2]*y[2];
  
  return y[0];
}

void loop() {
  if((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
    Serial.println('!');
  } else {
    // Take multiple readings
    float sum = 0;
    for(int i = 0; i < 4; i++) {
      sum += analogRead(ECG_PIN);
      delayMicroseconds(100);
    }
    float rawValue = sum / 4;
    
    // Apply Butterworth filter
    float filteredValue = butterworthFilter(rawValue);
    
    // Apply baseline correction
    static float baseline = 2048;
    baseline = 0.995 * baseline + 0.005 * filteredValue;
    filteredValue -= baseline;
    
    // Map to appropriate range
    int outputValue = map(filteredValue, -2048, 2048, 0, 4095);
    
    Serial.println(outputValue);
  }
  
  delay(5);  // 200Hz sampling rate
}













// // ESP32 ECG Monitor with AD8232
// // Pin Definitions
// const int ECG_PIN = 34;           // ADC pin for ECG signal
// const int LEADS_OFF_PLUS = 25;    // LO+ pin
// const int LEADS_OFF_MINUS = 26;   // LO- pin

// // Sampling Configuration
// const int SAMPLING_RATE = 250;    // 250 Hz sampling rate
// const int DELAY_TIME = 1000000/SAMPLING_RATE;  // Microseconds between samples

// // Digital Filter Parameters
// const int FILTER_ORDER = 2;
// const int BUFFER_SIZE = FILTER_ORDER + 1;

// // Butterworth bandpass filter coefficients (0.5 - 40 Hz)
// float b[] = {0.0154f, 0.0f, -0.0154f};  // Numerator coefficients
// float a[] = {1.0000f, -1.9692f, 0.9692f};  // Denominator coefficients

// // Circular buffers for filter
// float x[BUFFER_SIZE] = {0};  // Input buffer
// float y[BUFFER_SIZE] = {0};  // Output buffer

// // Moving average for baseline correction
// const int MA_SIZE = 25;
// float ma_buffer[MA_SIZE] = {0};
// int ma_index = 0;
// float ma_sum = 0;

// void setup() {
//   // Initialize serial communication
//   Serial.begin(115200);  // Increased baud rate for higher sampling rate
  
//   // Configure ADC
//   analogReadResolution(12);          // 12-bit resolution (0-4095)
//   analogSetWidth(12);               // Set ADC width to 12 bits
//   analogSetAttenuation(ADC_11db);   // Set ADC attenuation for larger voltage range
//   analogSetPinAttenuation(ECG_PIN, ADC_11db);
  
//   // Configure pins
//   pinMode(LEADS_OFF_PLUS, INPUT);   // Setup LO+ pin
//   pinMode(LEADS_OFF_MINUS, INPUT);  // Setup LO- pin
//   pinMode(ECG_PIN, INPUT);          // Setup ECG pin
  
//   // Wait for ADC to stabilize
//   delay(1000);
// }

// // Function to apply Butterworth filter
// float butterworthFilter(float input) {
//   // Shift input buffer
//   for(int i = BUFFER_SIZE-1; i > 0; i--) {
//     x[i] = x[i-1];
//   }
//   x[0] = input;
  
//   // Shift output buffer
//   for(int i = BUFFER_SIZE-1; i > 0; i--) {
//     y[i] = y[i-1];
//   }
  
//   // Apply filter
//   float output = 0;
//   for(int i = 0; i < BUFFER_SIZE; i++) {
//     output += b[i] * x[i];
//     if(i > 0) output -= a[i] * y[i-1];
//   }
  
//   y[0] = output;
//   return output;
// }

// // Function to update moving average
// float updateMovingAverage(float newValue) {
//   ma_sum -= ma_buffer[ma_index];
//   ma_buffer[ma_index] = newValue;
//   ma_sum += newValue;
//   ma_index = (ma_index + 1) % MA_SIZE;
//   return ma_sum / MA_SIZE;
// }

// void loop() {
//   static unsigned long lastSample = 0;
//   unsigned long currentTime = micros();
  
//   // Check if it's time for a new sample
//   if (currentTime - lastSample >= DELAY_TIME) {
//     lastSample = currentTime;
    
//     // Check if leads are connected
//     if((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//       Serial.println("!");  // Indicate leads are disconnected
//       return;
//     }
    
//     // Take multiple readings for noise reduction
//     float sum = 0;
//     for(int i = 0; i < 4; i++) {
//       sum += analogRead(ECG_PIN);
//       delayMicroseconds(50);
//     }
//     float rawValue = sum / 4;
    
//     // Apply Butterworth filter
//     float filteredValue = butterworthFilter(rawValue);
    
//     // Apply baseline correction using moving average
//     float baseline = updateMovingAverage(filteredValue);
//     filteredValue -= baseline;
    
//     // Scale the output to appropriate range (0-4095)
//     int outputValue = constrain(map(filteredValue, -2048, 2048, 0, 4095), 0, 4095);
    
//     // Send the value
//     Serial.println(outputValue);
//   }
// }











// Constants for filtering
// const int SAMPLES = 10;            // Number of samples for moving average
// const int LEADS_OFF_PLUS = 25;     // LO+ pin
// const int LEADS_OFF_MINUS = 26;    // LO- pin
// const int ECG_PIN = 34;           // ECG signal pin

// // Variables for filtering
// int readings[SAMPLES];
// int readIndex = 0;
// int total = 0;
// int average = 0;

// // Variables for additional filtering
// const float ALPHA = 0.1; // Smoothing factor for EMA filter
// float filteredValue = 0;

// void setup() {
//   Serial.begin(9600);
  
//   // Configure ADC
//   analogReadResolution(12);          // Set ADC resolution to 12 bits
//   analogSetAttenuation(ADC_11db);    // Set ADC attenuation
//   analogSetWidth(12);                // Ensure 12-bit sampling
  
//   // Setup pins
//   pinMode(LEADS_OFF_PLUS, INPUT);
//   pinMode(LEADS_OFF_MINUS, INPUT);
//   pinMode(ECG_PIN, INPUT);
  
//   // Initialize readings array
//   for (int i = 0; i < SAMPLES; i++) {
//     readings[i] = 0;
//   }
// }

// // Moving average filter
// int movingAverage(int newReading) {
//   total = total - readings[readIndex];
//   readings[readIndex] = newReading;
//   total = total + readings[readIndex];
//   readIndex = (readIndex + 1) % SAMPLES;
//   return total / SAMPLES;
// }

// // Exponential moving average filter
// float exponentialMovingAverage(float newValue) {
//   filteredValue = (ALPHA * newValue) + ((1 - ALPHA) * filteredValue);
//   return filteredValue;
// }

// // DC offset removal
// int removeDCOffset(int value, int baseline = 2048) {
//   return value - baseline;
// }

// void loop() {
//   if((digitalRead(LEADS_OFF_PLUS) == 1) || (digitalRead(LEADS_OFF_MINUS) == 1)) {
//     Serial.println('!');
//   } else {
//     // Multiple readings for stability
//     int sum = 0;
//     for(int i = 0; i < 4; i++) {
//       sum += analogRead(ECG_PIN);
//       delayMicroseconds(100);
//     }
//     int rawValue = sum / 4;
    
//     // Apply filters
//     int maValue = movingAverage(rawValue);                  // Moving average
//     float emaValue = exponentialMovingAverage(maValue);     // Exponential moving average
//     int finalValue = removeDCOffset(emaValue);              // Remove DC offset
    
//     // Map the value to a reasonable range (optional)
//     int mappedValue = map(finalValue, -2048, 2048, 0, 4095);
    
//     // Send the filtered value
//     Serial.println(mappedValue);
//   }
  
//   delay(10); // Adjust this value based on your needs (10ms = 100Hz sampling rate)
// }













































// void setup() {
//   // Initialize the serial communication:
//   Serial.begin(9600);

//   // Setup for leads off detection (choose appropriate GPIO pins):
//   pinMode(25, INPUT); // Replace with any available GPIO for LO+
//   pinMode(26, INPUT); // Replace with any available GPIO for LO-

//   // Initialize analog input (GPIO 34 in this case):
//   pinMode(34, INPUT); // Analog ECG signal pin
// }

// void loop() {
//   // Check if leads are off
//   if((digitalRead(25) == 1) || (digitalRead(26) == 1)) {    
//     Serial.println('!');  // Leads off warning
//   }
//   else {
//     // Read and send the ECG signal from GPIO 34:
//     int ecgValue = analogRead(34);
//     Serial.println(ecgValue);  // Send ECG data
//   }

//   // Wait a bit to prevent serial data saturation
//   delay(1);
// }


































// void setup() {
//   // Initialize the serial communication:
//   Serial.begin(9600);

//   // Setup for leads off detection (choose appropriate GPIO pins):
//   pinMode(25, INPUT); // Replace with any available GPIO for LO+
//   pinMode(26, INPUT); // Replace with any available GPIO for LO-

//   // Initialize analog input (GPIO 34 in this case):
//   pinMode(34, INPUT); // Analog ECG signal pin
// }

// void loop() {
//   // Check if leads are off
//   if((digitalRead(25) == 1) || (digitalRead(26) == 1)) {    
//     Serial.println('!');  // Leads off warning
//   }
//   else {
//     // Read and send the ECG signal from GPIO 34:
//     int ecgValue = analogRead(34);
//     Serial.println(ecgValue);  // Send ECG data
//   }

//   // Wait a bit to prevent serial data saturation
//   delay(1);
// }

