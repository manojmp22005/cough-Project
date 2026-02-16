/*
 * Cough Detection & BLE Notification
 * Board: Arduino Nano 33 BLE Sense
 * 
 * This sketch does two things:
 * 1. Runs a TinyML model to detect cough type (Mocked logic for demo).
 * 2. Advertises the result via BLE so the Python Gateway can pick it up.
 */

#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h> // For accelerometer if needed, generally useful to include
// #include <TensorFlowLite.h> // Uncomment when you have the Edge Impulse library installed

// --- BLE Settings ---
BLEService coughService("19B10000-E8F2-537E-4F6C-D104768A1214"); // Custom UUID
// Characteristic to send the cough type (Read & Notify)
BLEStringCharacteristic coughCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify, 20);

// --- State ---
String lastCough = "None";
unsigned long lastEventTime = 0;

void setup() {
  Serial.begin(9600);
  // while (!Serial); // Don't block if not connected to USB

  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // Setup BLE
  BLE.setLocalName("CoughMonitor");
  BLE.setAdvertisedService(coughService);
  coughService.addCharacteristic(coughCharacteristic);
  BLE.addService(coughService);
  
  // Initial Value
  coughCharacteristic.writeValue("Normal");
  
  BLE.advertise();
  Serial.println("Bluetooth device active, waiting for connections...");
  
  // Initialize Mic (simulated here)
  Serial.println("Microphone Initialized");
}

void loop() {
  BLEDevice central = BLE.central();

  // If a central (PC/Phone) is connected
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      
      // 1. Run Audio Classification Logic
      String detectedCough = runCoughInference();
      
      // 2. If cough logic returns something new/interesting
      if (detectedCough != "Normal" && detectedCough != lastCough) {
        // Debounce/Limit rate
        if (millis() - lastEventTime > 3000) { 
           Serial.print("Detected: ");
           Serial.println(detectedCough);
           
           // Update BLE Characteristic
           coughCharacteristic.writeValue(detectedCough);
           
           lastCough = detectedCough;
           lastEventTime = millis();
        }
      } else if (millis() - lastEventTime > 5000) {
        // Reset to normal after 5 seconds of silence
        lastCough = "Normal";
        coughCharacteristic.writeValue("Normal");
        lastEventTime = millis();
      }
      
      delay(100);
    }
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}

// --- Mock Inference Logic ---
// In a real Edge Impulse project, you would replace this with:
// ei_impulse_result_t result = { 0 };
// run_classifier(&signal, &result, debug_mode);
String runCoughInference() {
  // Simulate random coughs for demonstration
  // In real life, this function analyzes microphone buffer
  
  int randVal = random(0, 500); // reduced frequency
  if (randVal == 1) return "Dry Cough";
  if (randVal == 2) return "Wet Cough";
  if (randVal == 3) return "Whooping Cough";
  
  return "Normal";
}
