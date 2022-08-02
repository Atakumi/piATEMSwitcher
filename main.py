#!/usr/bin/env python3
# coding: utf-8

""" ATEM switcher controller for Raspberry Pi (3-)
Copyright by Takumi DRIVE OU / Takumi Amano """

from typing import Dict, Any
import sys
import time
import signal
import gpio_handler
import PyATEMMax
import pi_lcd

ip_address = "192.168.101.240"
key_interrupt  = False

# Create ATEMMax object
switcher = PyATEMMax.ATEMMax()

# Create GPIO button/led/lcd object
gpio   = gpio_handler.gpioall()
button = gpio_handler.button()
led    = gpio_handler.button_led()
lcd    = pi_lcd.gpiolcd()

VIDEO_LIST = ["input5", "input6", "mediaPlayer1"]
pvw_index = 99
pgm_index = 99

def terminate():
    switcher.disconnect()
    button.cleanup()
    led.cleanup()
    lcd.cleanup()
    gpio.cleanup()

def reflect_buttonled():
    global pvw_index, pgm_index
    # print("index:" + str(pvw_index) + "/" + str(pgm_index))
    pvw_name = switcher.previewInput[0].videoSource.name
    pgm_name = switcher.programInput[0].videoSource.name
    new_pvw_index = VIDEO_LIST.index(pvw_name) if pvw_name in VIDEO_LIST else 99
    if new_pvw_index != pvw_index:
        led.Green(pvw_index, 0)
        led.Green(new_pvw_index, 1)
        pvw_index = new_pvw_index
    new_pgm_index = VIDEO_LIST.index(pgm_name) if pgm_name in VIDEO_LIST else 99
    if new_pgm_index != pgm_index:
        led.Red(pgm_index, 0)
        led.Red(new_pgm_index, 1)
        pgm_index = new_pgm_index

def signal_handler(signal_number, frame):
    if key_interrupt:
        return     # already handled
    print("\nProcess terminated.")
    terminate()

def button_callback(btn):
    if switcher.connected != True:
        print("switcher is not connected")
        return
    if btn == 0:
        switcher.setPreviewInputVideoSource(0, 5)    # Set preview to source 5
    if btn == 1:
        switcher.setPreviewInputVideoSource(0, 6)    # Set preview to source 6
    if btn == 2:
        switcher.setPreviewInputVideoSource(0, "mediaPlayer1")    # Set preview to mp1
    if btn == 3:
        switcher.execAutoME(0)                       # Execute "Auto"

def onReceive(params: Dict[Any, Any]) -> None:
#    print(f"[{time.ctime()}] Received [{params['cmd']}]: {params['cmdName']}")
#    print(f"Intransition : {switcher.transition[0].inTransition}")
    if switcher.transition[0].inTransition:
        led.Red(3, 1)
    else:
        led.Red(3, 0)
    if params['cmd'] == "PrvI":
        reflect_buttonled()


if __name__ == "__main__":
    lcd.puts("ATEM Remote", 0)
    lcd.puts("   ver. 0.1", 1)
    time.sleep(2)
    try:
        # Connect
        lcd.puts(ip_address, 0)
        lcd.puts("Connecting..", 1)
        switcher.registerEvent(switcher.atem.events.receive, onReceive)
        switcher.connect(ip_address)
        switcher.waitForConnection()
        print("Connected.")
        lcd.puts("Connected.", 1)
        signal.signal(signal.SIGTERM, signal_handler)
        button.setcallback(button_callback)
        time.sleep(1)
        reflect_buttonled()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        key_interrupt = True
        print("\nbreak.")
    finally:
        terminate()
