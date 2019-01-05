# !/usr/bin/python3
#
# Back to the Future Clock
# Version 4
#
# CADJ 28/12/2018
#
# Thread 1: Display
# Thread 2: Control
# Player managed at the OS level using MPD/MPC
# Additional threads created by gpiozero for button control
#

# threading
import threading
import _thread

# OS and low-level
import time
import sys
from subprocess import call
import signal

# utilities
import csv
import re

# time control
import datetime
from datetime import datetime
from icu import ICUtzinfo

# Project-specific modules
import globals  # Overall configurations and global variables
import mpc  # player commands
from Display import *  # Control of the 16-digit alphanumeric display
from Buttons import *  # Button controls from GPIO pins
from Clock import *  # Time functions for the display
from Player import *  # MP3 player functions
from Weather import *  # Weather functions


def getParameters():
    """ Read parameters from the parameter file and override the defaults from globals.py
    """
    print("Reading parameter file {}".format(globals.paramFile))
    try:
        with open(globals.paramFile, 'r') as f:
            reader = csv.DictReader(filter(lambda line: line[0] != '#', f))
            for row in reader:
                globals.parameters[row['parameter']] = row['value']
        if 'MP3_Source' in globals.parameters.keys():
            globals.MP3_Source = globals.parameters['MP3_Source']
        if 'Deadline' in globals.parameters.keys():
            globals.Deadline = globals.parameters['Deadline']
        if 'MP3_Vol' in globals.parameters.keys():
            globals.MP3_Vol = int(globals.parameters['MP3_Vol'])
        if 'FromDate' in globals.parameters.keys():
            globals.FromDate = globals.parameters['FromDate']
        if 'DefaultClockMode' in globals.parameters.keys():
            globals.DefaultClockMode = int(globals.parameters['DefaultClockMode'])
        if 'Brightness' in globals.parameters.keys():
            globals.Brightness = int(globals.parameters['Brightness'])
        if 'MP3_Filter' in globals.parameters.keys():
            globals.MP3_Filter = globals.parameters['MP3_Filter'].strip()
        if 'RadioSource' in globals.parameters.keys():
            globals.RadioSource = globals.parameters['RadioSource']
        if 'RingtonesSource' in globals.parameters.keys():
            globals.RingtonesSource = globals.parameters['RingtonesSource']
        if 'RadioList' in globals.parameters.keys():
            globals.RadioList = globals.parameters['RadioList']
        if 'AlarmTone' in globals.parameters.keys():
            globals.AlarmTone = int(globals.parameters['AlarmTone'])
        if 'Locale' in globals.parameters.keys():
            globals.Locale = globals.parameters['Locale']
    except EnvironmentError:
        print("Parameters file not found, keeping defaults")

    print('MP3_Source: {}'.format(globals.MP3_Source))
    print('MP3_Vol: {}'.format(globals.MP3_Vol))
    print('MP3_Filter: {}'.format(globals.MP3_Filter))
    print('RadioSource: {}'.format(globals.RadioSource))
    print('RingtonesSource: {}'.format(globals.RingtonesSource))
    print('FromDate: {}'.format(globals.FromDate))
    print('Deadline: {}'.format(globals.Deadline))
    print('DefaultClockMode: {}'.format(globals.DefaultClockMode))
    print('Brightness: {}'.format(globals.Brightness))
    print('RadioList: {}'.format(globals.RadioList))
    print('AlarmTone: {}'.format(globals.AlarmTone))
    print('Locale: {}'.format(globals.Locale))

    print("Reading timezones file {}".format(globals.timezonesFile))
    try:
        with open(globals.timezonesFile, 'r') as f:
            for row in f:
                if row[0] != '#':
                    globals.TimeZones.append(re.split(';', row))
    except EnvironmentError:
        print("Timezones file not found, keeping only the local timezone")
        defaultTZ = ICUtzinfo.getDefault()
        globals.TimeZones.append(str(defaultTZ))


def shutdown():
    """ Executes shutdown when button 6 is held for more than 5 seconds
        Button 3 (OK) confirms; Button 5 cancels
    """
    clear_display16()
    print_str16('Shutdown? ')
    time.sleep(1)
    while not globals.B[3].is_pressed:
        if globals.B[5].is_pressed:
            break
        time.sleep(0.2)
    clear_display16()
    call('sudo shutdown +1', shell=True)
    sys.exit()


class ControlThread(threading.Thread):
    """ Key control thread
        For special button uses, global in relation to clock modes
    """

    def __init__(self):
        threading.Thread.__init__(self)
        print("Initializing control thread...")

    def run(self):
        while globals.running.is_set():
            if globals.B[2].is_pressed and globals.B[4].is_pressed:  # reload parameters file
                print("Reloading...")
                mpc.stop()
                mpc.clear()
                clear_display16()
                print_str16("Reloading...")
                write_display16()
                time.sleep(1)
                # actual reloading
                getParameters()
                globals.ClockMode = globals.DefaultClockMode
                set_brightness16(globals.Brightness)
                clear_display16()
                print_str16("Ready")
                write_display16()
                time.sleep(1)
                print("Done reloading.")

            if globals.B[1].is_pressed and globals.B[5].is_pressed:  # exit system
                if globals.ClockMode == 1:
                    clear_display16()
                    # time.sleep(0.5)
                    CM = globals.ClockMode
                    d0 = datetime.now()
                    while not globals.B[3].is_pressed and CM == globals.ClockMode:
                        print_str16("Terminate?      ")
                        write_display16()
                        time.sleep(0.5)
                        dt = datetime.now() - d0
                        if dt.total_seconds() > 5:
                            break
                        if globals.B[3].is_pressed:
                            globals.running.clear()
                            clear_display16()
                            cleanupButtons()
                            sys.exit()
            time.sleep(0.2)


class DisplayThread(threading.Thread):
    """ Display handling thread
        Calls the functions for each clock mode in turn, based on the global ClockMode variable
    """

    def __init__(self):
        threading.Thread.__init__(self)
        print("Initializing display thread, ClockMode = {}...".format(globals.ClockMode))

    def run(self):
        while globals.running.is_set():
            if globals.ClockMode == 1:
                try:
                    BTTF_Clock()
                except (KeyboardInterrupt, SystemExit):
                    clear_display16()
                    cleanupButtons()
                    globals.running.clear()
                    sys.exit()
            elif globals.ClockMode == 2:
                current_weather('SBBH')
            elif globals.ClockMode == 3:
                weather_forecast('222', 4)
            elif globals.ClockMode == 4:
                TimeSinceDate(globals.FromDate)
            elif globals.ClockMode == 5:
                TimeToDeadline(globals.Deadline)
            elif globals.ClockMode == 6:
                WorldClock()
            elif globals.ClockMode == 7:
                initMP3()
                init_MP3_playlist()
                try:
                    play_mp3()  # local files
                    time.sleep(0.2)
                except (KeyboardInterrupt, SystemExit):
                    mpc.stop()
                    mpc.clear()
                    clear_display16()
                    globals.running.clear()
                    sys.exit()
            elif globals.ClockMode == 8:
                initMP3()
                init_MP3_playlist(1)
                try:
                    play_mp3(1)  # Internet radio
                    time.sleep(0.2)
                except (KeyboardInterrupt, SystemExit):
                    mpc.stop()
                    mpc.clear()
                    clear_display16()
                    globals.running.clear()
                    sys.exit()
            elif globals.ClockMode == 9:
                Clock()
            elif globals.ClockMode == 10:
                Now_Milliseconds()
            elif globals.ClockMode == 11:
                Chrono()    # milliseconds chronometer
            elif globals.ClockMode == 12:
                Chrono(1)   # seconds chronometer
            elif globals.ClockMode == 13:
                setAlarm()
            elif globals.ClockMode == 14:
                Timer()
            else:
                globals.ClockMode = 1
            time.sleep(0.01)


button_hold_time = datetime.now()


def button_held():
    """ Callback for when the MODE button is held -- action will take place when it is released
    """
    global button_hold_time
    # gets the time for the button press
    button_hold_time = datetime.now()
    # print("Hold: {}".format(button_hold_time))


def change_mode():
    """ Change to the default clock mode with a long press
        Change to the next clock mode with a short press
    """
    global button_hold_time

    br = datetime.now()  # time for button release
    # print("Release: {}".format(br))
    td = br - button_hold_time  # timedelta object
    active_time = td.total_seconds()  # seconds pressed, float

    if active_time > 2.0:
        # print("Long press: {}".format(active_time))
        globals.ClockMode = globals.DefaultClockMode
    elif active_time < 0.2:
        # print("Short press: {}".format(active_time))
        globals.ClockMode += 1
    print("ClockMode: {}".format(globals.ClockMode))


def main():
    # initialization
    print("Reading parameters...")
    getParameters()

    print("Initializing display...")
    init16()

    print("Initializing buttons...")
    globals.B[0].when_pressed = button_held
    globals.B[0].when_released = change_mode

    # Threading start
    try:
        globals.ClockMode = globals.DefaultClockMode
        t1 = DisplayThread()
        t1.start()
        tc = ControlThread()
        tc.start()
        print("Running...")
        # signal.pause()
    except (KeyboardInterrupt, SystemExit):
        globals.running.clear()
        t1.join()
        tc.join()
        clear_display16()
        cleanupButtons()
        mpc.stop()
        mpc.clear()
        sys.exit()
    # finally:
    #    cleanupButtons()
    #    clear_display16()

    # while True:
    #    pass


if __name__ == '__main__':
    main()
