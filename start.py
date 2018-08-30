import RPi.GPIO as GPIO
import subprocess
import signal
import os
from time import sleep

SwitchButton = 4


GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#  GPIO.setup(SwitchButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SwitchButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#  GPIO.add_event_detect(SwitchButton, GPIO.RISING, callback=launch_poloboard)


# on definit notre fonction qui sera appelee quand on appuiera sur le bouton
def launch_poloboard(channel):
    GPIO.cleanup()
    # on lance la commande d extinction
    os.system('sudo python /home/pi/python/poloboard/poloboard.py')

GPIO.add_event_detect(SwitchButton, GPIO.RISING, callback=launch_poloboard)

rec_proc = None
try:
    while True:
       #if GPIO.input(SwitchButton) == GPIO.LOW:
       #     print "switch is on"
       #     if rec_proc is None:
       #         rec_proc = subprocess.Popen("/home/pi/python/poloboard/start.sh", shell=True, preexec_fn=os.setsid)
       # else:
       #     print "switch is off"
       #     if rec_proc is not None:
       #         os.killpg(rec_proc.pid, signal.SIGTERM)
       #         rec_proc = None
        sleep(0.2)

finally:
    GPIO.cleanup()