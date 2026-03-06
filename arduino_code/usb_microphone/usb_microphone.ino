/*
  Simple USB Microphone for Arduino Nano 33 BLE Sense
  Streams raw 16-bit PCM audio (16kHz) over USB Serial.
  
  AUTHOR: Manoj
  DATE: Feb 2026
*/

#include <PDM.h>

// Buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// Number of audio samples read
volatile int samplesRead;

void setup() {
  // Initialize Serial at high speed
  Serial.begin(460800); 
  while (!Serial);

  // Configure the data receive callback
  PDM.onReceive(onPDMdata);

  // Initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate
  if (!PDM.begin(1, 16000)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
}

void loop() {
  // Wait for samples to be read from PDM interrupt
  if (samplesRead) {
    // Write raw bytes to USB Serial
    // samplesRead is number of SAMPLES. Bytes = samples * 2.
    Serial.write((uint8_t *)sampleBuffer, samplesRead * 2);

    // Clear the read count
    samplesRead = 0;
  }
}

/* 
   Callback function to process the data from the PDM microphone.
   This runs in an interrupt context (background).
*/
void onPDMdata() {
  // Query the number of available bytes
  int bytesAvailable = PDM.available();

  // Read into the sample buffer
  PDM.read(sampleBuffer, bytesAvailable);

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}