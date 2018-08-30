import RPi.GPIO as GPIO
import signal
import subprocess
import os
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

rec_proc = None
try:
    while True:
        if GPIO.input(4):

            if rec_proc is None:
                rec_proc = subprocess.Popen("/script/start.sh",
                           shell=True, preexec_fn=os.setsid)
        else:

            if rec_proc is not None:
                os.killpg(rec_proc.pid, signal.SIGTERM)
                rec_proc = None
        sleep(0.2)

finally:
    GPIO.cleanup()