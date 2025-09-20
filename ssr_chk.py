#!/usr/bin/python3
#
import RPi.GPIO as GPIO
import time
import sys
#
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)  # side heater
GPIO.setup(12, GPIO.OUT)  # core heater
GPIO.setup(13, GPIO.OUT)  # heater
GPIO.setup(15, GPIO.OUT)  # pump
GPIO.setup(16, GPIO.OUT)  # side heater
GPIO.setup(18, GPIO.OUT)  # freezer
GPIO.setup(19, GPIO.OUT)  # bottom heater
#
on=1;off=0
#
while True:
  try:
#
    GPIO.output(int(sys.argv[1]), 1) # 250331
    time.sleep(1)
#
    GPIO.output(int(sys.argv[1]), 0) # 250331
    time.sleep(1)
  except KeyboardInterrupt:
    GPIO.output(11, False)
    GPIO.output(12, False)
    GPIO.output(13, False)
    GPIO.output(15, False)
    GPIO.output(16, False)  #0321
    GPIO.output(18, False)
    GPIO.output(19, False)
    exit()
