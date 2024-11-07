# simple image capturing software for a raspberry-cam
from picamera2 import Picamera2
import time

picam2 = Picamera2()

picam2.configure(picam2.create_still_configuration())
picam2.start()

picam2.capture_file("./input.jpg")

picam2.stop()
