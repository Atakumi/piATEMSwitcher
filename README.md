# piATEMSwitcher
ATEM Switcher controller on Raspberry Pi with GPIO physical switch.  
Just using existing library to access, but add some "programable" feature with hardware switch box.

## Prerequisites
- Raspberry Pi
  - 2/3/4/zero 2 W
  - (Zero W is not recommended - parsing packet is too heavy for single core. Verified with Zero 2 W and 3 B+)
- Raspi OS
  - 32bit, Light version is enough, but it should work on 64bit / GUI version
- Switch box hardware
  - You can design / build it as you like!
- Python library : [PyATEMMax](https://clvlabs.github.io/PyATEMMax/)

## GPIO connection to switch / LED / UPS or power switch(optional)

### NOTE: All port number is BCM standard

- Character LCD (SD1602 controller)
  - RS : 4
  - E  : 17
  - D4 : 27
  - D5 : 22
  - D6 : 10
  - D7 : 9
  - (R/W should be connected to ground)

- Switch 0
  - Red LED   : 12
  - Green LED : 16
  - Switch    : 26

- Switch 1
  - Red LED   : 8
  - Green LED : 0
  - Switch    : 1

- Switch 2
  - Red LED   : 23
  - Green LED : 24 
  - Switch    : 25

- Switch 3
  - Red LED   : 14
  - Green LED : 15
  - Switch    : 18

- Power off detector : 19
  - High - power on, holding low for 3 seconds - power off

## Description of each file

### main.py
- Main program

### pi_lcd.py / gpio_handler.py / util.py
- Sub functions (as class)

### events.py
- This is just an example of the library PyATEMMax, but useful to verify connection between the host environment to ATEM switcher

### atemconfig.json
- Configuration file to define each button function, display name and other parameters to be sent to the switcher.

### atemremote.sh
- Sample startup script

### atemremote.service
- Sample **systemd** service definition file. To invoke the program on Raspberry Pi start up, put this file into 
~~~
/etc/systemd/system
~~~
then enable auto-startup, by
~~~
raspi:~ $ sudo systemctl daemon-reload
raspi:~ $ sudo systemctl enable atomremote
~~~
so you would see it would run right after the Raspberry Pi starting up. See **systemd** document if you would like to customize for your environment.

Enjoy!!
