#!/usr/bin/env python2.7

# on importe les modules necessaires
import time
import os
import RPi.GPIO as GPIO

import Adafruit_CharLCD as LCD


# Setup RPi TPIC6B595N for 7 Segments Led displays
DATAIN = 26  # serin
LATCH = 13   # RCK
CLOCK = 6    # SRCK
CLEAR = 19   # SRCLR
OE = 4      # Output Enable Low

GPIO.setup(DATAIN, GPIO.OUT)
GPIO.setup(CLOCK, GPIO.OUT)
GPIO.setup(LATCH, GPIO.OUT)
GPIO.setup(CLEAR, GPIO.OUT)
GPIO.setup(OE, GPIO.OUT)


GPIO.output(LATCH, False)    # Latch is used to output the saved data
GPIO.output(CLEAR, True)     # Clear must always be true. False clears registers
GPIO.output(OE, False)       # Output Enable speaks for itself. Must be False to display
GPIO.output(CLOCK, False)    # Used to shift the value of DATAIN to the register
GPIO.output(DATAIN, False)   # Databit to be shifted into the register


# Setup led segments
init_message = [
    "00000100",  # i
    "01010100",  # n
    "00000100",  # i
    "01111000"   # t
]


def print_nothing():
    GPIO.output(LATCH, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in "00000000":
        GPIO.output(DATAIN, False)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    GPIO.output(LATCH, True)


# LCD pin setup
lcd_rs = 5
lcd_en = 11
lcd_d4 = 9
lcd_d5 = 10
lcd_d6 = 22
lcd_d7 = 17
lcd_backlight = 27

lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

lcd.clear()

lcd.set_cursor(0, 0)
lcd.message("Poloboard Ready!")
lcd.set_cursor(0, 1)
lcd.message("Swith to start")


print_nothing()

StartPoloboardSwitch = 4

GPIO.setmode(GPIO.BCM)

GPIO.setup(StartPoloboardSwitch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.add_event_detect(SwitchButton, GPIO.FALLING, callback=lambda a: launch_poloboard())

def launch_poloboard():
     print("Starting POLOBOARD!")
     GPIO.cleanup()
     os.system('sudo python /home/pi/python/poloboard/poloboard.py')


try:
    while 1:

        if GPIO.input(StartPoloboardSwitch) == GPIO.LOW:
            launch_poloboard()
        else:
            print("Ready to start POLOBOARD!")

    time.sleep(0.02)
finally:
     print_nothing()
     lcd.clear()
     GPIO.cleanup()