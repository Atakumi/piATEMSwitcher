#!/usr/bin/python
# coding: utf-8

""" ATEM switcher controller for Raspberry Pi (3-)
Copyright by Takumi DRIVE OU / Takumi Amano """

from typing import Dict, Any
import os
import sys
import time
import datetime
import signal
import logging
import threading
import gpio_handler
import PyATEMMax
import pi_lcd

ip_address = "192.168.101.240"
key_interrupt  = False

event = threading.Event()

logging.basicConfig( 
    filename='atemremote.log', encoding='utf-8',
    level=logging.INFO,
    datefmt='%H:%M:%S',
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s')

log = logging.getLogger('ATEM-REMOTE')

# Create ATEMMax object
switcher = PyATEMMax.ATEMMax()
# set log level
# switcher.setSocketLogLevel(logging.DEBUG)

# Create GPIO button/led/lcd object
gpio   = gpio_handler.gpioall()
button = gpio_handler.button()
led    = gpio_handler.button_led()
lcd    = pi_lcd.gpiolcd()


VIDEO_LIST = ["input5", "input6", "mediaPlayer1"]
SHORT_LABEL_LIST = ["SDI5", "SDI6", "MP1"]

pvw_index = 99
pgm_index = 99

def terminate():
    switcher.disconnect()
    button.cleanup()
    led.cleanup()
    lcd.cleanup()
    power.cleanup()
    gpio.cleanup()

def shutdown():
    global return_code
    log.info("Power button pushed.")
    lcd.puts("Shutting down", 0)
    lcd.puts("Wait 10 sec", 1)
    return_code = 1   ## shutdown after exiting the program
    event.set()       ## exit the loop

def reflect_buttonled():
    global pvw_index, pgm_index
    # log.info("index:" + str(pvw_index) + "/" + str(pgm_index))
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
    log.info("\nProcess terminated.")
    terminate()

def button_callback(btn):
    global connectedstate
    print("button:", btn)
    log.info("button:" + str(btn))
    if connectedstate != True:
        print("switcher is not connected")
        return
    if btn >= 0 and btn <= 2:
        print("sending preview command")
        switcher.setPreviewInputVideoSource(0, VIDEO_LIST[btn])    # Set preview to source 5
    if btn == 3:
        print("sending AUTO command")
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

def onConnect(params: Dict[Any, Any]) -> None:
    global connectedstate
    if connectedstate == False:
        connectedstate = True
        log.info("Connected.")
        lcd.puts("Connected.", 0)
        print("Connected.")
    reflect_buttonled()

def onDisconnect(params: Dict[Any, Any]) -> None:
    global connectedstate
    connectedstate = False
    log.info("Disconnected.")
    print("Disconnected.")
    lcd.puts("Reconnecting...", 0)

def show_time():
    timenow = datetime.datetime.now()
    timestr = format(timenow, '%H:%M:%S')
    lcd.puts(timestr, 0)

def thread_exception(args):
    print("catch the thread exception - ", args.exc_type)
    log.info("exception on other thread, as " + str(args.exc_type))
    lcd.puts("OS Error", 0)
    lcd.puts("Restarting", 1)
    return_code = 2   ## repeat invoking after exiting the program
    event.set()       ## exit the main loop

if __name__ == "__main__":
    threading.excepthook = thread_exception

    power = gpio_handler.powercheck(shutdown)
    connectedstate = False
    return_code = 2

    log.info("Started.")

    lcd.puts("ATEM Remote", 0)
    lcd.puts("   ver. 0.1", 1)
    time.sleep(2)

    lcd.clear()
    lcd.puts("Connecting..", 0)
    log.info("Connecting")

    switcher.registerEvent(switcher.atem.events.receive, onReceive)
    switcher.registerEvent(switcher.atem.events.connect, onConnect)
    switcher.registerEvent(switcher.atem.events.disconnect, onDisconnect)

    # switcher.atem.defaultConnectionTimeout = 5.0 # full connection: default 1.0 seconds
    # switcher.atem.defaultHandshakeTimeout  = 2.5 # basic handshake: default 0.1 seconds

    signal.signal(signal.SIGTERM, signal_handler)

    sourcetext = ""
    for src in SHORT_LABEL_LIST: 
        sourcetext += (src + " ")
    lcd.puts(sourcetext, 1)

    button.setcallback(button_callback)

    # Connect
    try:
        switcher.connect(ip_address, connTimeout = 10)
        event.wait()

    except KeyboardInterrupt:
        key_interrupt = True
        return_code = 0
        print("\nbreak.")
        lcd.clear()
        lcd.puts("Terminated.", 0)
        log.info("Terminated.")

    except Exception as ex:
        log.info("Exception occurs:", ex.__class__)
        lcd.puts("Error!", 0)
        lcd.puts("Rebooting", 1)
        return_code = 2  ## repeat invoking after exiting the program
        event.set()

    finally:
        print("return code - ", return_code)
        time.sleep(2)
        terminate()
        sys.exit(return_code)

