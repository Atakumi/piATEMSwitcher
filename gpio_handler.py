#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

GPIO_BUTTON_LIST = [26, 1, 25, 18]

class gpioall:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def cleanup(self):
        GPIO.cleanup()

class button:
    def __init__(self):
        GPIO.setup(GPIO_BUTTON_LIST, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        for port in GPIO_BUTTON_LIST:
            GPIO.add_event_detect(port, GPIO.RISING, callback=self.internal_callback, bouncetime=500)

    def setcallback(self, _callback):
        self.callback = _callback

    def internal_callback(self, e):
#        print("arg: " + str(e))
        self.callback(GPIO_BUTTON_LIST.index(e))

    def cleanup(self):
        for port in GPIO_BUTTON_LIST:
            GPIO.remove_event_detect(port)

GPIO_LED_DIC = {0:{'R':12, 'G':16}, 1:{'R':8, 'G':0}, 2:{'R':23, 'G':24}, 3:{'R':14, 'G':15}} 

class button_led:
    def __init__(self):
        all_leds = list(GPIO_LED_DIC.values())
        for leds in all_leds:
            # print(leds['R'])
            GPIO.setup(leds['R'], GPIO.OUT)
            GPIO.output(leds['R'], GPIO.HIGH)
            # print(leds['G'])
            GPIO.setup(leds['G'], GPIO.OUT)
            GPIO.output(leds['G'], GPIO.HIGH)

    def Red(self, num, value):
        if num >= len(GPIO_LED_DIC):
            return
        if value > 0:
            GPIO.output(GPIO_LED_DIC[num]['R'], GPIO.LOW)
        else:
            GPIO.output(GPIO_LED_DIC[num]['R'], GPIO.HIGH)

    def Green(self, num, value):
        if num >= len(GPIO_LED_DIC):
            return
        if value > 0:
            GPIO.output(GPIO_LED_DIC[num]['G'], GPIO.LOW)
        else:
            GPIO.output(GPIO_LED_DIC[num]['G'], GPIO.HIGH)

    def cleanup(self):
        return
         
def callback_example(btn):
    print("Button " + str(btn) + " pushed.")

if __name__ == "__main__":
    gpio = gpioall()
    btn = button()
    btn.setcallback(callback_example)
    led = button_led()
    try:
        while True:
            for i in range(4):
                time.sleep(0.5)
                led.Red(i, 1)
                time.sleep(0.5)
                led.Red(i, 0)
                time.sleep(0.5)
                led.Green(i, 1)
                time.sleep(0.5)
                led.Green(i, 0)
    except KeyboardInterrupt:
        print("\nbreak.")
        led.cleanup()
        btn.cleanup()
        gpio.cleanup()
