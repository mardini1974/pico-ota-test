
# app.py - initial version
import time

VERSION = "1.0.0"

def run():
    print("OTA TEST")
    print("Running version:", VERSION)

    while True:
        print("Pico application:", VERSION)
        time.sleep(5)
