#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

GPIO_BUTTON_LIST = [6, 13, 19, 26, 16, 20, 21]

class button:
    def __init__(self):
        self.setupGPIO()

    def setcallback(self, _callback):
        self.callback = _callback

    def internal_callback(self, e):
#        print("arg: " + str(e))
        self.callback(GPIO_BUTTON_LIST.index(e))

    def setupGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON_LIST, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for port in GPIO_BUTTON_LIST:
            GPIO.add_event_detect(port, GPIO.FALLING, callback=self.internal_callback, bouncetime=500)

    def cleanup(self):
        for port in GPIO_BUTTON_LIST:
            GPIO.remove_event_detect(port)
        GPIO.cleanup()

GPIO_LED_LIST = [0, 1, 5]

class rgbled:
    def __init__(self):
        GPIO.setup(GPIO_LED_LIST, GPIO.OUT)
        GPIO.output(GPIO_LED_LIST, GPIO.HIGH)

    def Red(self, value):
        if value > 0:
            GPIO.output(0, GPIO.LOW)
        else:
            GPIO.output(0, GPIO.HIGH)

    def Green(self, value):
        if value > 0:
            GPIO.output(5, GPIO.LOW)
        else:
            GPIO.output(5, GPIO.HIGH)

    def Blue(self, value):
        if value > 0:
            GPIO.output(1, GPIO.LOW)
        else:
            GPIO.output(1, GPIO.HIGH)

    def RGB(self, r, g, b):
        self.Red(r)
        self.Green(g)
        self.Blue(b)

    
def callback_example(btn):
    print("Button " + str(btn) + " pushed.")

if __name__ == "__main__":
    btn = button()
    btn.setcallback(callback_example)
    led = rgbled()
    try:
        while True:
            time.sleep(0.5)
            led.Red(1)
            time.sleep(0.5)
            led.Red(0)
            time.sleep(0.5)
            led.Green(1)
            time.sleep(0.5)
            led.Green(0)
            time.sleep(0.5)
            led.Blue(1)
            time.sleep(0.5)
            led.Blue(0)
    except KeyboardInterrupt:
        print("\nbreak.")
        btn.cleanup()
