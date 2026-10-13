import time
from machine import Pin

VERSION = "1.0.6"
led = Pin("LED", Pin.OUT)

def run():
    for i in range(3):
        led.on()
        time.sleep(0.3)
        led.off()
        time.sleep(0.3)

    print("Running version:", VERSION)

    while True:
        time.sleep(5)
