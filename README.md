# piATEMSwitcher
ATEM Switcher controller on Raspberry Pi with GPIO physical switch

## prerequisite
- Raspberry Pi (2/3/4/zero W)
- Raspi OS

- Switch box hardware

- Python library : PyATEMMax

## GPIO connection to switch / LED / UPS(optional)

### NOTE: All port number is BCM standard

- Character LCD (SD1602 controller)
  RS : 4
  E  : 17
  D4 : 27
  D5 : 22
  D6 : 10
  D7 : 9
  (R/W should be connected to ground)

- Switch 0
  Red LED   : 12
  Green LED : 16
  Switch    : 26

- Switch 1
  Red LED   : 8
  Green LED : 0
  Switch    : 1

- Switch 2
  Red LED   : 23
  Green LED : 24 
  Switch    : 25

- Switch 3
  Red LED   : 14
  Green LED : 15
  Switch    : 18

- Power off detector : 19
  (High - power on, Low - power off)


