import time
import random
import logging
from db_utils import init_db, log_cough

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [EDGE DEVICE] - %(message)s')

# Initialize DB (simulating connection to cloud/server)
init_db()

COUGH_TYPES = ["Dry Cough", "Wet Cough", "Whooping Cough", "Croup", "Normal"]

def record_audio():
    """
    Simulates recording audio for 5 seconds.
    In real implementation: use pyaudio or sounddevice.
    """
    logging.info("🎤 Listening for audio...")
    time.sleep(2) # Simulating recording time
    return "sample_audio.wav"

def mock_inference(audio_file):
    """
    Simulates running a TFLite model on the audio.
    In real implementation: 
    1. Load model: interpreter = tf.lite.Interpreter(model_path="model.tflite")
    2. Preprocess audio (MFCCs/Spectrogram)
    3. interpreter.invoke()
    """
    logging.info("🧠 Processing audio with AI model...")
    time.sleep(1) # Simulating inference time
    
    # 30% chance of detecting a cough to make it realistic
    if random.random() < 0.3:
        detected_type = random.choice(COUGH_TYPES)
        confidence = round(random.uniform(0.7, 0.99), 2)
        return detected_type, confidence
    return None, 0

def run_edge_device():
    logging.info("🚀 Cough Detection Hardware Started")
    logging.info("Waiting for sound events...")
    
    try:
        while True:
            # Simulate "Wait for trigger" or continuous loop
            audio = record_audio()
            
            result, confidence = mock_inference(audio)
            
            if result and result != "Normal":
                logging.info(f"⚠️ DETECTED: {result} ({confidence*100}%)")
                logging.info(f"📡 Transmitting data to Cloud Dashboard...")
                log_cough(result, confidence)
                logging.info("✅ Data sent!")
            else:
                logging.info("🟢 No cough detected.")
                
            time.sleep(3) # Wait before next cycle

    except KeyboardInterrupt:
        logging.info("🛑 Hardware stopped.")

if __name__ == "__main__":
    run_edge_device()
