import serial
import time
import re
from db_utils import log_cough

# CONFIGURATION
SERIAL_PORT = 'COM3'  # You might need to change this to your Arduino's COM port
BAUD_RATE = 115200

def parse_arduino_line(line):
    """
    Parses a line from the Arduino Serial output.
    Expected formats from Edge Impulse examples:
    - "cough: 0.98"
    - "Prediction: cough (0.95)"
    - "Classes: noise, cough"
    """
    line = line.strip().lower()
    
    # Check for simple "label: confidence" format
    # Example: "cough: 0.95"
    if "cough" in line and ":" in line:
        parts = line.split(":")
        label = parts[0].strip()
        try:
            confidence = float(parts[1].strip())
            return label, confidence
        except ValueError:
            pass
            
    return None, 0.0

def run_serial_gateway():
    print(f"🔌 Connecting to Arduino on {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("✅ Connected! Listening for coughs...")
        
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    # print(f"Raw: {line}") # Uncomment to debug raw output
                    
                    label, confidence = parse_arduino_line(line)
                    
                    if label == "cough":
                        if confidence > 0.70: # 70% threshold
                            print(f"🚨 COUGH DETECTED! Confidence: {confidence:.2f}")
                            log_cough("Cough", confidence)
                        else:
                            print(f"Cough detected but low confidence: {confidence:.2f}")
                            
                except UnicodeDecodeError:
                    pass # Ignore bad bytes
                    
            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"❌ Error: Could not connect to {SERIAL_PORT}.")
        print("   Make sure the Arduino is plugged in and you are not using the Serial Monitor in Arduino IDE.")
        print(f"   Details: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Gateway stopped.")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    run_serial_gateway()
