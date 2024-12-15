import time
import csv
from smbus2 import SMBus
import board
import adafruit_bme280

from send_data import send_data

# Initialize the BME280 sensor
i2c = board.I2C()  # Uses board's I²C pins
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Class for GY-273 (HMC5883L) compass sensor
class GY273Compass:
    def __init__(self, bus_number=1, address=0x1E):
        self.bus = SMBus(bus_number)
        self.address = address
        self.initialize_sensor()

    def initialize_sensor(self):
        # Set up the sensor (Configuration register A: 0x00, Mode register: 0x02)
        self.bus.write_byte_data(self.address, 0x00, 0x70)  # 8-average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, 0x01, 0xA0)  # Gain = 5
        self.bus.write_byte_data(self.address, 0x02, 0x00)  # Continuous measurement mode

    def read_raw_data(self, reg):
        # Read two bytes of data from the specified register
        data = self.bus.read_i2c_block_data(self.address, reg, 2)
        return data[0] << 8 | data[1]

    def read_compass(self):
        try:
            x = self.read_raw_data(0x03)  # X-axis MSB, LSB
            z = self.read_raw_data(0x05)  # Z-axis MSB, LSB
            y = self.read_raw_data(0x07)  # Y-axis MSB, LSB
            if x >= 0x8000: x -= 0x10000  # Convert to signed 16-bit
            if y >= 0x8000: y -= 0x10000
            if z >= 0x8000: z -= 0x10000
            return x, y, z
        except Exception as e:
            print(f"Error reading compass: {e}")
            return 0, 0, 0  # Default to zero on failure


# Initialize the GY-273 compass sensor
try:
    compass = GY273Compass()
    use_compass = True
except Exception as e:
    print(f"Failed to initialize GY-273: {e}")
    use_compass = False

# Set up CSV file
csv_filename = "sensor_data.csv"

# Create or open the CSV file and write the header if needed
with open(csv_filename, mode="a", newline="") as file:
    writer = csv.writer(file)
    file.seek(0, 2)  # Move to the end of the file
    if file.tell() == 0:  # If the file is empty, write the header
        writer.writerow([
            "Timestamp",
            "Temperature (C)",
            "Humidity (%)",
            "Pressure (hPa)",
            "Compass X",
            "Compass Y",
            "Compass Z"
        ])

# Function to log data
def read_sensors():
    """Read in data from BME280 and GY273 sensors"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # BME280 readings
    temperature = bme280.temperature
    humidity = bme280.humidity
    pressure = bme280.pressure

    # Compass readings
    if use_compass:
        compass_x, compass_y, compass_z = compass.read_compass()
    else:
        compass_x, compass_y, compass_z = 0, 0, 0  # Default to zero if compass is unavailable

    print(f"{timestamp}: Temp={temperature:.2f}C, Humidity={humidity:.2f}%, Pressure={pressure:.2f}hPa, "
          f"Compass(X={compass_x}, Y={compass_y}, Z={compass_z})")

    return temperature, humidity, pressure, compass_x, compass_y, compass_z

def log_data(temperature, humidity, pressure, compass_x, compass_y, compass_z):
    """Save data to csv file"""
    with open(csv_filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write data to CSV
        writer.writerow([timestamp, temperature, humidity, pressure, compass_x, compass_y, compass_z])

# Main loop
print("Logging data. Press Ctrl+C to stop.")
try:
    while True:
        temperature, humidity, pressure, compass_x, compass_y, compass_z = read_sensors()
        log_data(temperature, humidity, pressure, compass_x, compass_y, compass_z)
        send_data(temperature, humidity, pressure, compass_x, compass_y, compass_z)
        
        time.sleep(1)  # Adjust the interval as needed
except KeyboardInterrupt:
    print("Data logging stopped.")
