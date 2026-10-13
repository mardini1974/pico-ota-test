
# app.py - version 1.0.0
import time

VERSION = "1.0.0"

def run(confirm):
    print("Application version:", VERSION)

    # Startup self-test
    time.sleep(2)
    confirm()

    while True:
        print("Running version", VERSION)
        time.sleep(5)
