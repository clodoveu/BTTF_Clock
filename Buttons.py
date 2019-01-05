# !/usr/bin/python3
#
# Back to the Future Clock
# Buttons functions
# Version 4
#
# CADJ 28/12/2018
#
#

# Raspberry Pi & hardware-related
from gpiozero import Button

# Project-specific modules
import globals

#
# Global hardware setup and initialization
#

# GPIO pins and buttons
"""
B0 = 12 # MODE button
B1 = 22 ## REW / RESET button
B2 = 23 ## VOL- button
B3 = 24 ## PLAY-PAUSE / GO button
B4 = 25 ## VOL+ button / STOP button
B5 = 27 ## FWD button

BUZZ = 13 ## Buzzer
"""


#
# INITIALIZATION
#
# see globals.py

def initButtons():
    """ Initialize buttons as to the gpiozero library
    """
    globals.B[0] = Button(12, hold_time=0.2, hold_repeat=True)
    globals.B[1] = Button(22)
    globals.B[2] = Button(23)
    globals.B[3] = Button(24)
    globals.B[4] = Button(25)
    globals.B[5] = Button(27)


def cleanupButtons():
    """ Clean up button assignments as to the gpiozero library
    """
    for x in globals.B:
        x.close()
