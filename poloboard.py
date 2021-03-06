#!/usr/bin/python

import RPi.GPIO as GPIO
import time
from time import sleep
import Adafruit_CharLCD as LCD
import subprocess



# =================================================


# GPIO Setup
GPIO.cleanup()
GPIO.setwarnings(False)



#  Variables
time_formats = [10, 12, 15, 20]
index_time_format = 0
time_left = time_formats[index_time_format]*60  # sets default to 10 minutes game
time_total = time_left
timer_started = False

goals = {}
goals['left'] = 0
goals['right'] = 0


# Raspberry Pi pin setup
lcd_rs = 5
lcd_en = 11
lcd_d4 = 9
lcd_d5 = 10
lcd_d6 = 22
lcd_d7 = 17
lcd_backlight = 27

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

lcd.clear()

#  Buttons

StartStopButton = 21

ResetButton = 24
SelectTimeButton = 25

LedGreen = 20
LedRed = 16

RightPlusButton = 14
RightMinusButton = 15
LeftPlusButton = 18
LeftMinusButton = 23

RebootButton = 12

GPIO.setup(RebootButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # reboot button
GPIO.setup(StartStopButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # start stop button

GPIO.setup(SelectTimeButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(ResetButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button

GPIO.setup(RightPlusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(RightMinusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(LeftPlusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(LeftMinusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button

GPIO.add_event_detect(RightPlusButton, GPIO.FALLING, callback=lambda a: add_goal('right'), bouncetime=500)
GPIO.add_event_detect(RightMinusButton, GPIO.FALLING, callback=lambda b: remove_goal('right'), bouncetime=500)
GPIO.add_event_detect(LeftPlusButton, GPIO.FALLING, callback=lambda e: add_goal('left'), bouncetime=500)
GPIO.add_event_detect(LeftMinusButton, GPIO.FALLING, callback=lambda f: remove_goal('left'), bouncetime=500)

GPIO.add_event_detect(RebootButton, GPIO.FALLING, callback=lambda r: reboot(), bouncetime=200)

GPIO.add_event_detect(SelectTimeButton, GPIO.FALLING, callback=lambda c: select_time(), bouncetime=200)
GPIO.add_event_detect(ResetButton, GPIO.FALLING, callback=lambda d: reset_match(), bouncetime=200)

GPIO.setup(LedRed, GPIO.OUT)  # red led
GPIO.setup(LedGreen, GPIO.OUT)  # green led


# Setup RPi TPIC6B595N for TIMER
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

numbers = [
    "10111111",  # 0
    "10000110",  # 1
    "11011011",  # 2
    "11001111",  # 3
    "11100110",  # 4
    "11101101",  # 5
    "11111101",  # 6
    "10000111",  # 7
    "11111111",  # 8
    "11101111",  # 9
    "10000000",  # null
]


# =================================================

def reboot():
    print "Stop requested, Halting the RPi now!"

    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.message("Rebooting...")

    subprocess.call(['reboot'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def select_time():
    global index_time_format
    global time_left
    global timer_started

    if timer_started == False:

        time_left = time_formats[index_time_format]*60
        if len(time_formats) > index_time_format+1:
            index_time_format += 1
        else:
            index_time_format = 0

        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.message("Time limit:")
        lcd.set_cursor(0, 1)
        lcd.message(str (time_formats[index_time_format]) + ' minutes')

        print ('\rTime limit is now set to : ' + str (time_formats[index_time_format]) + ' minutes.')  # console
        print_to_lcd()
        print_to_leds()
        sleep(0.5)

    return time_left, index_time_format


def reset_match():
    if timer_started == False:
        global goals
        global index_time_format
        global time_left
        global index_time_format
        # index_time_format = 0
        goals['left'] = 0
        goals['right'] = 0
        time_left = time_total
        print('Reset Time and Goals')
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.message("Reset")

        print_time_and_score()
        print_to_lcd()
        print_to_leds()


def print_time_and_score():
    print('\r\r --- ---  ---  ---  ---  ---  ---  --- ')
    print('\r - Time Left : ' + print_time_converted(time_left))
    print('\r - Left : ' + str(goals['left']))
    print('\r - Right : ' + str(goals['right']))
    print('\r --- ---  ---  ---  ---  ---  ---  --- \r')


def add_goal(side):
    global goals
    if goals[side] <= 9:
        goals[side] += 1
    else:
        goals[side] = 0

    print_to_console('+1')
    print_to_lcd()
    print_to_leds()


def remove_goal(side):
    global goals
    if goals[side] > 0:
        goals[side] -= 1
    else:
        goals[side] = 9

    print_to_console('-1')
    print_to_lcd()
    print_to_leds()


def print_time_converted(time_in_seconds):
    m, s = divmod(time_in_seconds, 60)
    time_hr  = str(m).zfill(2) + ":" + str(s).zfill(2)
    return time_hr


def print_to_console(msg=time_left):
    print(msg)


def print_message():
    print('Press button to select time 10, 12, 15 or 20 minutes game')


def print_to_lcd():
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.message(print_time_converted(time_left))
    lcd.set_cursor(0, 1)
    lcd.message("L: " + str(goals['left']) + "    |   R: " + str(goals['right']))


def print_to_leds():
    global time_left
    global goals
    gr = goals['right']
    gl = goals['left']

    m, s = divmod(time_left, 60)
    secs = str(s)
    mins = str(m)

    secs_d = int(secs[:1]) if s >= 10 else 0
    secs_u = int(secs[1:]) if s >= 10 else s
    mins_d = int(mins[:1]) if m >= 10 else 10
    mins_u = int(mins[1:]) if m >= 10 else m


    GPIO.output(LATCH, False)
    # goals
    for i in numbers[gl]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in numbers[gr]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    # timer
    for i in numbers[secs_u]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in numbers[secs_d]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for k, i in enumerate(numbers[mins_u]):
        #  print i
        if k == 0:
            GPIO.output(DATAIN, True)  # will always print the 2 dots between minutes and seconds
        else:
            GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in numbers[mins_d]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    GPIO.output(LATCH, True)


def stopwatch():
    global time_left
    global timer_started
    # print('\rStarted')
    switch_leds(True,False)
    while time_left >= 0:
        print print_time_converted(time_left)
        print_to_lcd()
        print_to_leds()
        if time_left<=10:
            GPIO.output(LedGreen, True)
            GPIO.output(LedRed, False)
            time.sleep(0.25)
            GPIO.output(LedGreen, False)
            GPIO.output(LedRed, True)
            time.sleep(0.25)
            GPIO.output(LedGreen, True)
            GPIO.output(LedRed, False)
            time.sleep(0.25)
            GPIO.output(LedGreen, False)
            GPIO.output(LedRed, True)
            time.sleep(0.25)
            break
        else:
            time.sleep(1)
        timer_started = True
        time_left -= 1
        if GPIO.input(StartStopButton) == GPIO.HIGH:
            switch_leds(False,True)
            print('\rPaused')
            #blink()
            break

    return time_left


def switch_leds(g,r):
    GPIO.output(LedGreen, g)
    GPIO.output(LedRed, r)


while True:
    try:

        #print_message()
        stopwatch()

        while True:
            if GPIO.input(StartStopButton) == GPIO.LOW:
                time_left = stopwatch()
                timer_started = True
            else:
                timer_started = False

    except KeyboardInterrupt:
        print "\rExit"
        lcd.clear()
        GPIO.cleanup()
        break