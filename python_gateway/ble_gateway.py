import asyncio
import logging
from bleak import BleakScanner, BleakClient
from db_utils import init_db, log_cough

# BLE UUIDs matching the Arduino Sketch
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BLE GATEWAY] - %(message)s')

# Initialize DB
init_db()

current_cough_state = "Normal"

def notification_handler(sender, data):
    """Callback triggered when Arduino sends a new notification."""
    global current_cough_state
    
    # Decode byte array to string
    try:
        cough_text = data.decode('utf-8')
    except:
        cough_text = "Unknown"
        
    logging.info(f"🔔 Received from Arduino: {cough_text}")
    
    # Only log meaningful coughs, ignore "Normal" updates unless needed
    if cough_text != "Normal" and cough_text != current_cough_state:
        logging.info(f"💾 Saving to Database: {cough_text}")
        log_cough(cough_text, confidence=0.95)
        
    current_cough_state = cough_text

async def run_ble_gateway():
    logging.info("Scanning for 'CoughMonitor'...")
    
    device = None
    
    while device is None:
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == "CoughMonitor":
                device = d
                logging.info(f"✅ Found Device: {d.name} ({d.address})")
                break
        if not device:
            await asyncio.sleep(2)
            print(".", end="", flush=True)
            
    try:
        async with BleakClient(device.address) as client:
            logging.info(f"🔗 Connected to {device.name}")
            
            # Subscribe to notifications
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            
            logging.info("Waiting for data... (Press Ctrl+C to stop)")
            
            # Keep the script running to listen
            while True:
                await asyncio.sleep(1)
                
    except Exception as e:
        logging.error(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_ble_gateway())
    except KeyboardInterrupt:
        logging.info("Gateway stopped.")
