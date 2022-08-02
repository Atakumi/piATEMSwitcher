#Drivee16x2 LCD screen with Raspberry Pi
#Tutorial : http://osoyoo.com/?p=832

#import
import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 4
LCD_E  = 17 
LCD_D4 = 27
LCD_D5 = 22 
LCD_D6 = 10
LCD_D7 = 9


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

class gpiolcd:

  def __init__(self):
    GPIO.setup(LCD_E, GPIO.OUT)  # Enable
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    # Initialise display
    self.init()

  def init(self):
    # Initialise display
    self.sendbyte(0x33,LCD_CMD) # 110011 Initialise
    self.sendbyte(0x32,LCD_CMD) # 110010 Initialise
    self.sendbyte(0x06,LCD_CMD) # 000110 Cursor move direction
    self.sendbyte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
    self.sendbyte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    self.sendbyte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

  def sendbyte(self, bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command
    GPIO.output(LCD_RS, mode) # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
      GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
      GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
      GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
      GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    self.toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
      GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
      GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
      GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
      GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    self.toggle_enable()


  def toggle_enable(self):
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)


  def puts(self, message, line):
    if line == 0:
        lcd_line = LCD_LINE_1
    else:
        lcd_line = LCD_LINE_2
    message = message.ljust(LCD_WIDTH," ")
    self.sendbyte(lcd_line, LCD_CMD)
    for i in range(LCD_WIDTH):
      self.sendbyte(ord(message[i]),LCD_CHR)


  def clear(self):
    self.sendbyte(0x01, LCD_CMD)


  def cleanup(self):
    self.clear()


if __name__ == '__main__':

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

  lcd = gpiolcd()
  try:
    while True:
      # Send some test
      lcd.puts("LCD work with", 0)
      lcd.puts("Raspberry Pi!", 1)
      time.sleep(3) # 3 second delay

      # Send some text
      lcd.puts("Designed by ", 0)
      lcd.puts("osoyoo.com", 1)
      time.sleep(3) # 3 second delay

      # Send some text
      lcd.puts("Read Tutorial: ", 0)
      lcd.puts("osoyoo.com", 1)
      time.sleep(3)
  except KeyboardInterrupt:
    pass
  finally:
    lcd.cleanup()
    GPIO.cleanup()
