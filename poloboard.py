#!/usr/bin/python

import RPi.GPIO as GPIO
import time
from time import sleep

# LCD
import Adafruit_CharLCD as LCD



goals = {}
goals['left'] = 0
goals['right'] = 0


print('Press button to select time 10, 12, 15 or 20 minutes game')

#  Variables
time_formats = [10, 12, 15, 20]
index_time_format = 0
time_left = time_formats[index_time_format]*60  # sets default to 10 minutes game
time_total = time_left
timer_started = False


# GPIO Setup
GPIO.setwarnings(True)


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

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

lcd.clear()

#  Buttons

StartStopButton = 21

ResetButton = 14
SelectTimeButton = 15

LedGreen = 20
LedRed = 16

RightPlusButton = 12
RightMinusButton = 7

GPIO.setup(StartStopButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # start stop button

GPIO.setup(SelectTimeButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(ResetButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button

GPIO.setup(RightPlusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button
GPIO.setup(RightMinusButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button

GPIO.add_event_detect(RightPlusButton, GPIO.BOTH, callback=lambda a: add_goal('right'), bouncetime=100)
GPIO.add_event_detect(RightMinusButton, GPIO.BOTH, callback=lambda b: remove_goal('right'), bouncetime=100)

GPIO.add_event_detect(SelectTimeButton, GPIO.BOTH, callback=lambda c: select_time(), bouncetime=1000)
GPIO.add_event_detect(ResetButton, GPIO.BOTH, callback=lambda d: reset_match(), bouncetime=500)

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
    "00000100",
    "01010100",
    "00000100",
    "01111000"
]

nothing_message = [
    "00000000",
    "00000000",
    "00000000",
    "00000000",
]
numbers = [
    "00111111",  # 0
    "00000110",  # 1
    "01011011",  # 2
    "01001111",  # 3
    "01100110",  # 4
    "01101101",  # 5
    "01111101",  # 6
    "00000111",  # 7
    "01111111",  # 8
    "01101111",  # 9
    "00000000",  # null
]



# =================================================

def select_time():
    global index_time_format
    global time_left

    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.message("Time limit:")

    if timer_started == False:
        print ('\rTime limit is now set to : ' + str (time_formats[index_time_format]) + ' minutes.')

        lcd.set_cursor(0, 1)
        lcd.message(str (time_formats[index_time_format]) + ' minutes')
        print_to_leds()

        time_left = time_formats[index_time_format]*60
        if len(time_formats) > index_time_format+1:
            index_time_format += 1
        else:
            index_time_format = 0

    return time_left, index_time_format


def reset_match():
    goals['left'] = 0
    goals['right'] = 0
    global time_left
    time_left = time_total
    print('Reset Time and Goals')
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.message("Reset")
    print_to_leds()
    print_time_and_score()

def print_time_and_score():

    print('\r\r --- ---  ---  ---  ---  ---  ---  --- ')
    print('\r - Time Left : ' + print_time_converted(time_left))
    print('\r - Left : ' + str(goals['left']))
    print('\r - Right : ' + str(goals['right']))
    print('\r --- ---  ---  ---  ---  ---  ---  --- \r')

def print_time_converted(time_in_seconds):
    m, s = divmod(time_in_seconds, 60)
    time_hr  = str(m).zfill(2) + ":" + str(s).zfill(2)
    return time_hr

def print_to_lcd():
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.message(print_time_converted(time_left))
    lcd.set_cursor(0, 1)
    lcd.message("L: " + str(goals['left']) + "    |   R: " + str(goals['right']))


def add_goal(side):
    global goals_right
    global goals_left
    if goals[side] <= 9:
        goals[side] += 1
    else:
        goals[side] = O
    #print 'add goal to ' + side


def remove_goal(side):
    global goals_right
    global goals_left
    if goals[side] > 0:
        goals[side] -= 1
    #print 'add goal to ' - side


def print_message():
    GPIO.output(LATCH, False)
    for i in init_message[3]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in init_message[2]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in init_message[1]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in init_message[0]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    GPIO.output(LATCH, True)


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
    GPIO.output(LATCH, True)

def print_to_leds():
    global goals
    global time_left
    m, s = divmod(time_left, 60)
    secs = str(s)
    mins = str(m)
    secs_d = int(secs[:1]) if s >= 10 else 0
    secs_u = int(secs[1:]) if s >= 10 else s
    mins_d = int(mins[:1]) if m >= 10 else 10
    mins_u = int(mins[1:]) if m >= 10 else m
    print(str(mins_d) + str(mins_u) + ":" + str(secs_d) + str(secs_u))  # print to console

    GPIO.output(LATCH, False)
# goals

    gr = goals['right']
    gl = goals['left']
    for i in numbers[gr]:
        GPIO.output(DATAIN, False if i == "0" else True)
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
    for i in numbers[gl]:
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
    for i in numbers[mins_u]:
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
    # print('\rStarted')
    switch_leds(True,False)
    while time_left >= 0:
        # print print_time_converted(time_left)

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

        time_left -= 1

        if GPIO.input(StartStopButton) == GPIO.HIGH:
            switch_leds(False,True)
            print('\rPaused')
            #blink()
            break

    return time_left

def blink():
    print_to_leds()
    sleep(0.25)
    print_nothing()
    sleep(0.25)

def switch_leds(g,r):
    GPIO.output(LedGreen, g)
    GPIO.output(LedRed, r)
    timer_started = True if g == True else False



while True:

    try:
        print_message()
        #print_goals()

        # Setup time in seconds
        # input = int(raw_input("Enter time limit (10) : ") or "10")
        #input = 12
        #time_left = input * 60
        stopwatch()

        #print_msg()
        #time_left = abs(int(time_total))

        while True:
            if GPIO.input(StartStopButton) == GPIO.LOW:
                time_left = stopwatch()

    except KeyboardInterrupt:
        print "\rExit"
        lcd.clear()
        GPIO.cleanup()
        break

