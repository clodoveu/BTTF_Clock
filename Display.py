# !/usr/bin/python3
#
# Back to the Future Clock
# Display functions
# Version 4
#
# CADJ 28/12/2018
#
#

# These functions assume a set of four units of Adafruit's
# Quad Alphanumeric Display - Red 0.54" Digits w/ I2C Backpack
# arranged in line to form a 16-digit alphanumeric display
# Product ref: https://www.adafruit.com/product/1911

# Threading
import threading

# OS and low-level
import time

# Physical display arrangement and addressing
# d3   d2   d1   d0
# 3    2    1    0
# 0123 0123 0123 0123
# string positions: pos16
# 0000 0000 0011 1111
# 0123 4567 8901 2345


# Raspberry Pi & hardware-related
# Basic library for Adafruit's Quad displays
from Adafruit_LED_Backpack import AlphaNum4

#
# GLOBALS
#
import globals

# global list of display objects
d = []

#
# Global hardware setup and initialization
#
# hardwired I2C display addresses
addr_d0 = 0x70
addr_d1 = 0x72
addr_d2 = 0x71
addr_d3 = 0x73


#
# INITIALIZATION
#

def init16():
    """ Initialize all four displays, and set list d
    """
    global d
    d.append(AlphaNum4.AlphaNum4(address=addr_d0, busnum=1))
    d.append(AlphaNum4.AlphaNum4(address=addr_d1, busnum=1))
    d.append(AlphaNum4.AlphaNum4(address=addr_d2, busnum=1))
    d.append(AlphaNum4.AlphaNum4(address=addr_d3, busnum=1))
    for i in range(0, 4):
        d[i].begin()
        d[i].clear()
        d[i].set_brightness(globals.Brightness)


def set_digit16(pos16, digit, decimal_point=False):
    """ Set the digit at position pos16,
        turning on the decimal point or not
        pos16 counts left to right 0->15
    """
    dev = 3 - pos16 // 4
    index = pos16 % 4
    d[dev].set_digit(index, digit, decimal_point)


def clear_digit16(pos16):
    """ Clears the digit at position pos16,
        and clears the decimal point
        pos16 counts left to right 0->15
    """
    dev = 3 - pos16 // 4
    index = pos16 % 4
    d[dev].set_digit(index, ' ', False)


def clear_decimal_point16(pos16):
    """ Clears the decimal point at pos16
        pos16 counts left to right 0->15
    """
    dev = 3 - pos16 // 4
    index = pos16 % 4
    d[dev].set_decimal(index, False)


def set_decimal_point16(pos16):
    """ Turns on the decimal point at pos16
        pos16 counts left to right 0->15
    """
    dev = 3 - pos16 // 4
    index = pos16 % 4
    d[dev].set_decimal(index, True)


def clear_display16():
    """ Clears the contents of the 16 digits
    """
    for i in range(0, 4):
        d[i].clear()
    write_display16()


def write_display16():
    """ Writes the display buffer to the hardware
    """
    for i in range(0, 4):
        d[i].write_display()


def set_brightness16(br=15):
    """ Sets the brightness of the display, range 0-15,
        default: maximum brightness
    """
    for i in range(0, 4):
        d[i].set_brightness(br)


def print_str16(value, justify_right=False):
    """ Prints the string to the 16-digit display
        Calculate starting position of digits based on justification.
    """
    pos = (16 - len(value)) if justify_right else 0
    # Go through each character and print it on the display.
    for i, ch in enumerate(value):
        set_digit16(i + pos, ch)


def print_time(tstr, justify_left=False):
    """ Prints a min.sec string in the four rightmost (default)
        or leftmost 4 digits, with decimal point)
    """
    pos = 0 if justify_left else 12
    # Go through each character in the time string
    for i, ch in enumerate(tstr):
        set_digit16(i + pos, ch)
    if justify_left:
        set_decimal_point16(1)
        d[0].write_display()
    else:
        set_decimal_point16(13)
        d[3].write_display()


class ScrollDisplayThread(threading.Thread):
    """ Thread to run a scrolling message across the 16-digit display
        width defines the number of positions to use for scrolling
        When width < 16, some digits may be left for other simultaneous use
    """

    def __init__(self, msg, width=16):
        threading.Thread.__init__(self)
        self.msg = msg
        self.width = width
        self.stop = False

    def run(self):
        pos = 0
        while (not self.stop) and (len(self.msg) > 0):
            for i in range(self.width):
                set_digit16(i, self.msg[(i + pos) % len(self.msg)])
            pos += 1
            pos = pos % len(self.msg)
            write_display16()
            time.sleep(0.1)

