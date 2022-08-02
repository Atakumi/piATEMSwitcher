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

ip_address = "192.168.101.240"
key_interrupt  = False

# Create ATEMMax object
switcher = PyATEMMax.ATEMMax()

# Create GPIO button/led object
button = gpio_handler.button()
led    = gpio_handler.rgbled()

def terminate():
    led.Blue(0)
    switcher.disconnect()
    button.cleanup()

def signal_handler(signal_number, frame):
    if key_interrupt:
        return     # already handled
    print("\nProcess terminated.")
    terminate()

def button_callback(btn):
#     print("button " + str(btn) + " pushed.")
    if switcher.connected != True:
        print("switcher is not connected")
        return
    if btn == 4:
        switcher.setPreviewInputVideoSource(0, 5)    # Set preview to source 5
    if btn == 5:
        switcher.setPreviewInputVideoSource(0, 6)    # Set preview to source 6
    if btn == 2:
        switcher.setPreviewInputVideoSource(0, "mediaPlayer1")    # Set preview to mp1
    if btn == 3:
        switcher.setPreviewInputVideoSource(0, "mediaPlayer2")    # Set preview to mp2
    if btn == 6:
        switcher.execAutoME(0)                       # Execute "Auto"
#        led.Blue(0)
#        led.Red(1)

def onReceive(params: Dict[Any, Any]) -> None:
#    print(f"[{time.ctime()}] Received [{params['cmd']}]: {params['cmdName']}")
#    print(f"Intransition : {switcher.transition[0].inTransition}")
    if switcher.transition[0].inTransition:
        led.Red(1)
        led.Blue(0)
    else:
        led.Red(0)
        led.Blue(1)

if __name__ == "__main__":
    led.Green(1)
    try:
        # Connect
        switcher.registerEvent(switcher.atem.events.receive, onReceive)
        switcher.connect(ip_address)
        switcher.waitForConnection()
        led.Green(0)
        print("Connected.")
        signal.signal(signal.SIGTERM, signal_handler)
        button.setcallback(button_callback)
        led.Blue(1)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        key_interrupt = True
        print("\nbreak.")
        terminate()
    
