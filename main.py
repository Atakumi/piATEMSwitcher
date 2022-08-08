#!/usr/bin/python
# coding: utf-8

""" 
    ATEM switcher controller for Raspberry Pi (ZeroW, 3-)
    Copyright by Takumi DRIVE OU / Takumi Amano 
"""

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
import util

event = threading.Event()
config = util.ReadConfig()

logging.basicConfig( 
    filename='atemremote.log', encoding='utf-8',
    level=logging.INFO,
    datefmt='%H:%M:%S',
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s')

log = logging.getLogger('ATEM-REMOTE')

# Create ATEMMax object
switcher = PyATEMMax.ATEMMax()
# set packet log level
# switcher.setSocketLogLevel(logging.DEBUG)

# Create GPIO button/led/lcd object
gpio   = gpio_handler.gpioall()
button = gpio_handler.button()
led    = gpio_handler.button_led()
lcd    = pi_lcd.gpiolcd()

# preset variables/list from config values
IP_ADDRESS = config.getIpAddress()
FUNC_LIST  = config.getButtonList("function")
SOURCE_LIST = config.getButtonList("source")
LABEL_LIST = config.getButtonList("display-name")

key_interrupt  = False
never_connected = True
pvw_index = 99
pgm_index = 99


def cleanupAll():
    try:
        switcher.disconnect()
        button.cleanup()
        led.cleanup()
        lcd.cleanup()
        power.cleanup()
        gpio.cleanup()
    except:
        pass          ## we all ignore exception occured during cleanup process


def reflect_buttonled():
    global pvw_index, pgm_index
    # log.info("index:" + str(pvw_index) + "/" + str(pgm_index))
    pvw_name = switcher.previewInput[0].videoSource.name
    pgm_name = switcher.programInput[0].videoSource.name
    new_pvw_index = SOURCE_LIST.index(pvw_name) if pvw_name in SOURCE_LIST else 99
    if new_pvw_index != pvw_index:
        led.Green(pvw_index, 0)
        led.Green(new_pvw_index, 1)
        pvw_index = new_pvw_index
    new_pgm_index = SOURCE_LIST.index(pgm_name) if pgm_name in SOURCE_LIST else 99
    if new_pgm_index != pgm_index:
        led.Red(pgm_index, 0)
        led.Red(new_pgm_index, 1)
        pgm_index = new_pgm_index

##
##  All event handlers
##

def onShutdownPushed():
    global return_code
    log.info("Power button pushed.")
    lcd.puts("Shutting down", 0)
    lcd.puts("Wait 10 sec", 1)
    return_code = 1   ## shutdown after exiting the program
    event.set()       ## exit the loop


def onSignalFromOS(signal_number, frame):
    if key_interrupt:
        return     # already handled
    return_code = 0
    lcd.clear()
    log.info("Process terminated.")
    cleanupAll()


def onButtonPushed(btn):
    global connectedstate
    print("button:", btn, " pushed")
    log.info("button:" + str(btn))
    if connectedstate != True:
        print("switcher is not connected")
        log.info("switcher is not connected")
        return

    btn_info = config.getButton(btn)
    if btn >= 0 and btn < len(FUNC_LIST):
        btn_func = FUNC_LIST[btn]
        if btn_func == "preview":
            print("sending preview command")
            switcher.setPreviewInputVideoSource(0, SOURCE_LIST[btn])    # Set source to Preview Out
        if btn_func == "program":
            print("sending program command")
            switcher.setProgramInputVideoSource(0, SOURCE_LIST[btn])    # Set source to PGM Out
        if btn_func == "aux":
            print("sending AUX command")
            switcher.setAuxSourceInput(0, SOURCE_LIST[btn])             # Set source to Aux Out
        if btn_func == "auto":
            print("sending AUTO command")
            switcher.execAutoME(0)
        if btn_func == "cut":
            print("sending CUT command")
            switcher.execCutME(0)
        if btn_func == "ftb":
            print("sending Fade to Black command")
            switcher.execFadeToBlackME(0)
        if btn_func == "runmacro":
            print("sending Run Macro command")
            macro_name = btn_info["macro-name"]
            switcher.setMacroAction(macro_name, swicher.atem.macroActions.runMacro)


def onReceive(params: Dict[Any, Any]) -> None:
#    print(f"[{time.ctime()}] Received [{params['cmd']}]: {params['cmdName']}")
#    print(f"Intransition : {switcher.transition[0].inTransition}")
    btn_index = FUNC_LIST.index("auto") if "auto" in FUNC_LIST else -1
    if btn_index >= 0:
        if switcher.transition[0].inTransition:
            led.Red(btn_index, 1)
        else:
            led.Red(btn_index, 0)
    if params['cmd'] == "PrvI":
        reflect_buttonled()


def onConnect(params: Dict[Any, Any]) -> None:
    global connectedstate, never_connected
    if connectedstate == False:
        connectedstate = True
        log.info("Connected.")
        lcd.puts("Connected.", 0)
        print("Connected.")
    reflect_buttonled()
    if never_connected:
        never_connected = False
        sourcetext = ""
        for src in LABEL_LIST: 
            sourcetext += src
        lcd.puts(sourcetext, 1)


def onDisconnect(params: Dict[Any, Any]) -> None:
    global connectedstate
    connectedstate = False
    log.info("Disconnected.")
    print("Disconnected.")
    lcd.puts("Reconnecting...", 0)


def onThreadException(args):
    print("catch the thread exception - ", args.exc_type)
    log.info("exception on other thread, as " + str(args.exc_type))
    lcd.puts("OS Error", 0)
    lcd.puts("Restarting", 1)
    return_code = 2   ## repeat invoking after exiting the program
    event.set()       ## exit the main loop


if __name__ == "__main__":
    threading.excepthook = onThreadException

    power = gpio_handler.powercheck(onShutdownPushed)
    connectedstate = False
    return_code = 2

    log.info("#### Started ####")

    lcd.puts("ATEM Remote", 0)
    lcd.puts("   ver. 0.1", 1)
    time.sleep(2)

    log.info("Connecting to " + IP_ADDRESS)

    lcd.clear()
    lcd.puts("Connecting..", 0)
    lcd.puts(IP_ADDRESS,     1)

    switcher.registerEvent(switcher.atem.events.receive,    onReceive)
    switcher.registerEvent(switcher.atem.events.connect,    onConnect)
    switcher.registerEvent(switcher.atem.events.disconnect, onDisconnect)

    # switcher.atem.defaultConnectionTimeout = 5.0 # full connection: default 1.0 seconds
    # switcher.atem.defaultHandshakeTimeout  = 2.5 # basic handshake: default 0.1 seconds

    signal.signal(signal.SIGTERM, onSignalFromOS)
    button.setcallback(onButtonPushed)

    # Connect
    try:
        switcher.connect(IP_ADDRESS, connTimeout = 5)
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
        cleanupAll()
        sys.exit(return_code)

