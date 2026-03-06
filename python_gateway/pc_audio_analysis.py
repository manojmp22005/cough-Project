"""
Arduino USB Microphone Audio Recorder
=====================================
Reads raw 16-bit PCM audio from Arduino Nano 33 BLE Sense
via USB Serial (using the usb_microphone.ino sketch).

IMPORTANT: You MUST upload 'usb_microphone.ino' to the Arduino first!
If you see text output like "cough: 0.95", you have the WRONG sketch uploaded.
"""
import wave
import time
import os
import sys
import numpy as np
import serial
import serial.tools.list_ports
import time

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_utils import log_cough

# ============================================================
# CONFIGURATION
# ============================================================
SERIAL_PORT = 'COM19'
BAUD_RATE = 460800
ARDUINO_SAMPLE_RATE = 16000
MAX_RECORD_SECONDS = 10


def normalize_audio(audio_data):
    """Normalize audio to prevent clipping."""
    peak = np.max(np.abs(audio_data))
    if peak == 0:
        return audio_data
    target_peak = int(32767 * 0.9)
    scale_factor = target_peak / peak
    if scale_factor < 1.0:
        return np.int16(audio_data.astype(np.float64) * scale_factor)
    elif peak < 1000:
        boost = min(scale_factor, 10.0)
        return np.int16(audio_data.astype(np.float64) * boost)
    return audio_data


def save_wav(filename, audio_data):
    """Save numpy audio array as a WAV file."""
    audio_data = normalize_audio(audio_data)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(ARDUINO_SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())
    duration = len(audio_data) / ARDUINO_SAMPLE_RATE
    print(f"  Saved: {filename} ({duration:.1f}s, {len(audio_data)} samples)")
    return True


def check_for_wrong_sketch(ser):
    """
    Check if the Arduino is sending text (wrong sketch) instead of binary audio.
    Returns True if WRONG sketch is detected.
    """
    print("  Checking data format...")
    try:
        # Read a small chunk
        data = ser.read(1000)
        if len(data) == 0:
            print("  [?] No data received. Is the Arduino streaming?")
            return False
            
        # Try to decode as text
        text = data.decode('utf-8', errors='ignore')
        if "cough" in text or "noise" in text or "Predictions" in text:
            print("\n" + "!" * 60)
            print("  [ERROR] WRONG ARDUINO SKETCH DETECTED!")
            print("  The Arduino is sending text classifications (e.g. 'cough: 0.8'),")
            print("  but this script expects RAW AUDIO bytes.")
            print()
            print("  SOLUTION: Upload 'usb_microphone.ino' to the Arduino.")
            print("!" * 60 + "\n")
            return True
            
        # Check data rate (approximate)
        if len(data) < 100:
            print(f"  [!] Data rate very low ({len(data)} bytes). Expected streaming audio.")
            return True
            
        print("  [OK] Data looks like raw audio (binary).")
        return False
    except Exception as e:
        print(f"  Check failed: {e}")
        return False


def run_recorder():
    print("=" * 50)
    print("  COUGH MONITOR - Arduino USB Microphone")
    print("=" * 50)
    print(f"  Port: {SERIAL_PORT} | Baud: {BAUD_RATE}")
    print(f"  Sample Rate: {ARDUINO_SAMPLE_RATE} Hz")
    print("=" * 50)
    print()

    # ========================================
    # MAIN SUPER LOOP (Reconnection)
    # ========================================
    while True:
        # 1. Connect to Arduino
        ser = None
        while ser is None:
            try:
                # Auto-detect port
                port_to_use = SERIAL_PORT
                import serial.tools.list_ports
                while True:
                    ports = list(serial.tools.list_ports.comports())
                    found = False
                    print(f"Scanning {len(ports)} ports...")
                    for p in ports:
                        desc = (p.description or "").lower()
                        mfr = (p.manufacturer or "").lower()
                        if "arduino" in desc or "nano" in desc or "arduino" in mfr or "usb serial" in desc:
                            port_to_use = p.device
                            found = True
                            break
                    
                    if found:
                        print(f"Auto-detected Arduino on {port_to_use}...")
                        break
                    else:
                        print(f"  Arduino not found. Retrying in 2s...")
                        time.sleep(2)

                ser = serial.Serial(port_to_use, BAUD_RATE, timeout=0.1)
                time.sleep(2)  # Wait for Arduino reset
                ser.reset_input_buffer()
                print("Connected!")
                
                # 2. Verify Sketch
                if check_for_wrong_sketch(ser):
                    ser.close()
                    ser = None
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                print(f"Connection failed: {e}")
                time.sleep(5)

        print()
        print("Ready! Waiting for 'Start Recording' from web app...")
        print()

        # ========================================
        # RECORDING LOOP
        # ========================================
        while True:
            try:
                # Drain buffer while idle
                if ser.in_waiting:
                    ser.read(ser.in_waiting)

                # Check command
                if os.path.exists("recording_status.txt"):
                    with open("recording_status.txt", "r") as f:
                        cmd = f.read().strip()
                    
                    if cmd == "START":
                        # Force reconnect to ensure fresh state for every recording
                        print("  Refreshing connection...")
                        try:
                            ser.close()
                            time.sleep(0.5)
                            ser.open()
                            ser.reset_input_buffer()
                        except:
                            # If reconnect fails, try full reconnect
                            try: ser.close()
                            except: pass
                            ser = None
                            print("  Connection lost during refresh. Reconnecting...")
                            # Let the outer loop handle full reconnect
                            break

                        print("\n*** RECORDING (10s)...")
                        
                        # Capture Audio
                        buffer = bytearray()
                        start_time = time.time()
                        last_debug = time.time()
                        
                        print(f"  Started capture at {start_time}")
                        
                        while time.time() - start_time < MAX_RECORD_SECONDS:
                            if ser.in_waiting:
                                chunk = ser.read(ser.in_waiting)
                                buffer.extend(chunk)
                            
                            # Debug print every 2 seconds
                            if time.time() - last_debug > 2:
                                print(f"    ... capturing (current bytes: {len(buffer)})")
                                last_debug = time.time()
                                
                            time.sleep(0.005) # fast poll
                            
                            # Stop if STOP command appears
                            if os.path.exists("recording_status.txt"):
                                with open("recording_status.txt") as f:
                                    if f.read().strip() == "STOP":
                                        break
                        
                        # Save regardless of size for debugging
                        print(f"  Captured Total: {len(buffer)} bytes.")
                        
                        # PRINT THE CONTENT TO SHOW USER
                        try:
                            print("-" * 30)
                            print("DATA PREVIEW (First 100 bytes):")
                            preview = buffer[:100]
                            print(f"Raw Hex: {preview.hex()}")
                            try:
                                print(f"As Text: {preview.decode('utf-8', errors='ignore')}")
                            except: pass
                            print("-" * 30)
                        except: pass

                        if len(buffer) > 0:
                            # Ensure even bytes
                            if len(buffer) % 2 != 0: buffer = buffer[:-1]
                            
                            audio = np.frombuffer(buffer, dtype=np.int16)
                            save_wav(f"manual_record_{int(time.time())}.wav", audio)
                            log_cough("Audio Recorded", 1.0)
                            print("  [OK] Saved (forced)!")
                        else:
                            print("  [X] Capture failed (0 bytes).")
                        
                        # Reset
                        try: os.remove("recording_status.txt") 
                        except: pass
                        print("Waiting...")

                time.sleep(0.2)

            except KeyboardInterrupt:
                return
            except Exception as e:
                print(f"Error: {e}")
                try: ser.close()
                except: pass
                break # Break inner loop, continue outer loop (reconnect)

if __name__ == "__main__":
    run_recorder()
