import serial

# LoRa settings
LORA_PORT = "/dev/ttyS0"  # Adjust depending on your setup, could be "/dev/ttyAMA0" or another UART port
LORA_BAUDRATE = 9600  # Default baud rate for Grove LoRa Radio

# Initialize the LoRa module
try:
    lora = serial.Serial(LORA_PORT, LORA_BAUDRATE, timeout=1)
    print(f"Connected to LoRa module on {LORA_PORT} at {LORA_BAUDRATE} baud.")
except Exception as e:
    print(f"Failed to connect to LoRa module: {e}")
    exit(1)

def send_data(data):
    """Send data over LoRa."""
    if not lora.is_open:
        print("LoRa serial port is not open.")
        return

    try:
        lora.write(data.encode('utf-8'))
        print(f"Sent: {data}")
    except Exception as e:
        print(f"Error sending data: {e}")