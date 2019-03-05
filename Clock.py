# !/usr/bin/python3
#
# Back to the Future Clock
# Clock functions
# Version 4
#
# CADJ 28/12/2018
#
#

# threading
import threading

# OS and low-level
import time

# Time control
import datetime
from datetime import datetime
from datetime import timedelta
from icu import Locale, DateFormat, ICUtzinfo, TimeZone

# Project-specific
import globals
import mpc
from Display import *
from Buttons import *


# CLOCK-RELATED FUNCTIONS

def td_format_seconds(td_object):
    """ Formats a 14-digit string from a timedelta object
        Years -> seconds
        Returns 99Y999d99h99.99
        Spaces to the left are not included, so the return value is of variable size
        Example: 14d18h30.01
    """
    seconds = int(td_object.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)

    msg = ''
    flag = False
    if years != 0:
        msg = '{0:2d}Y'.format(years)
        flag = True
    if days != 0 or flag:
        msg += '{0:3d}d'.format(days)
    if hours != 0 or flag:
        msg += '{0:2d}h'.format(hours)
    if hours > 0 or flag:
        msg += '{0:02d}{1:02d}'.format(minutes, seconds)
    else:
        msg += "{0:2d}{1:02d}".format(minutes, seconds)

    return msg


def td_format_seconds_6(td_object):
    """ Formats a 6-digit string from a timedelta object
        Hours -> seconds; input must be < 10h
        Returns 9h99.99
    """
    seconds = int(td_object.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    msg = ''
    if hours != 0:
        msg += '{0:1d}h'.format(hours)
    if hours > 0:
        msg += '{0:02d}{1:02d}'.format(minutes, seconds)
    else:
        msg += "{0:2d}{1:02d}".format(minutes, seconds)

    return msg


def td_format_milliseconds(td_object):
    """ Formats a 16-digit string from a timedelta object
        Days -> milliseconds
    """
    days = td_object.days
    seconds = td_object.seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milli = td_object.microseconds // 1000
    if minutes == 0 and hours == 0 and days == 0:
        return "{:2}{:03}".format(seconds, milli)
    if hours == 0 and days == 0:
        return "{:2}m{:02}{:03}".format(minutes, seconds, milli)
    if days == 0:
        return "{:2}h{:02}m{:02}{:03}".format(hours, minutes, seconds, milli)
    return "{}d{:02}h{:02}m{:02}{:03}".format(days, hours, minutes, seconds, milli)


def TimeSinceDate(date, layout='%Y-%m-%d %H:%M'):
    """ Prints the time since a given date in the 16-digit display
        Notice the input format
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode:
        d1 = datetime.strptime(date, layout)
        d0 = datetime.now()
        print_str16("{:>16}".format(td_format_seconds(d0 - d1)), True)
        set_decimal_point16(13)
        write_display16()
        time.sleep(0.5)


def TimeToDeadline(date, layout='%Y-%m-%d %H:%M'):
    """ Prints the time remaining to a given deadline in the 16-digit display
        Notice the input format.
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode:
        d1 = datetime.strptime(date, layout)
        d0 = datetime.now()
        print_str16("{:>16}".format(td_format_seconds(abs(d1 - d0))), True)
        set_decimal_point16(13)
        write_display16()
        time.sleep(0.5)


def Chrono(mode=0):
    """ A millisecond chronometer (mode = 0)
        or seconds chronometer (mode != 0)
        Controls:
        Button 3 = go
        Button 4 = stop
        Button 1 = reset
        Button 0 exits the chronometer for another clock mode
    """
    clear_display16()
    CM = globals.ClockMode  # detect change in MODE
    while CM == globals.ClockMode:
        t0 = datetime.now()
        if mode == 0:
            print_str16(td_format_milliseconds(t0 - t0), True)
            set_decimal_point16(12)
        else:
            print_str16("{:>16}".format(td_format_seconds(t0 - t0)), True)
            set_decimal_point16(13)
        write_display16()

        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):  # Wait for GO
            time.sleep(0.1)

        t0 = datetime.now()
        while (not globals.B[4].is_pressed) and (CM == globals.ClockMode):  # Running: STOP and MODE interrupt
            t1 = datetime.now()
            if mode == 0:
                print_str16(td_format_milliseconds(t1 - t0), True)
                set_decimal_point16(12)
            else:
                print_str16("{:>16}".format(td_format_seconds(t1 - t0)), True)
                set_decimal_point16(13)
            write_display16()

            time.sleep(0.001)
        time.sleep(0.2)

        while (not globals.B[1].is_pressed) and (CM == globals.ClockMode):  # Waiting for RESET or MODE change
            time.sleep(0.2)

        # if RESET, restart the loop
        # if MODE changed, exit the loop and the thread will redirect


def Now_Milliseconds():
    """ Prints the current time up to the millisecond
        in the 16-digit display
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode:
        d0 = datetime.now()
        print_str16(d0.strftime("%d/%m %Hh%M%S%f")[:-3], True)
        set_decimal_point16(12)
        set_decimal_point16(10)
        write_display16()
        time.sleep(0.001)


def Clock():
    """ Prints the current date, day of the week and time up to the second
        in the 16-digit display
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode:
        d0 = datetime.now()
        print_str16(d0.strftime("%a %d/%m %H%M%S").upper())
        set_decimal_point16(11)
        set_decimal_point16(13)
        write_display16()
        time.sleep(0.5)


def BTTF_Clock():
    """ Prints the current date and time in the Back to the Future format
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode and globals.running.is_set():
        d0 = datetime.now()
        print_str16(d0.strftime("%b %d %Y %H%M").upper())
        set_decimal_point16(13)
        write_display16()
        time.sleep(1)


def get_ip():
    """ Get the device's IP address using hostname command
    """
    ip = subprocess.check_output(["hostname", "-I"]).split()[0].decode('utf-8')
    print("IP address: {}".format(ip))
    return ip


def showIP():
    """ Displays the current IP address
    """
    CM = globals.ClockMode
    while CM == globals.ClockMode:
        # get device's IP address and display it
        print_str16(get_ip())
        write_display16()
        time.sleep(1)


def setAlarm():
    """ Sets an alarm time and activates the AlarmClock thread
    """
    # print Alarm in the display
    clear_display16()
    dt0 = datetime.now()

    alarm = [dt0.minute, dt0.hour, dt0.month, dt0.day]
    year = dt0.year
    lower_limit = [0, 0, 1, 1]
    upper_limit = [60, 24, 12, 31]
    msg = ['Min  ', 'Hour ', 'Month', 'Day  ', 'Set  ']

    # get alarm time from the keys
    pos = 0
    print_str16("{4:5} {0:02}/{1:02} {2:02}{3:02}".format(alarm[3], alarm[2], alarm[1], alarm[0], msg[0]))
    set_decimal_point16(13)
    write_display16()
    CM = globals.ClockMode
    while pos < 4 and CM == globals.ClockMode:
        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):
            if globals.B[2].is_pressed:
                alarm[pos] -= 1
            if globals.B[4].is_pressed:
                alarm[pos] += 1
            if alarm[pos] < lower_limit[pos]:
                alarm[pos] = upper_limit[pos] - 1 + lower_limit[pos]
            if alarm[pos] > upper_limit[pos]:
                alarm[pos] = lower_limit[pos]
            print_str16("{4:5} {0:02}/{1:02} {2:02}{3:02}".format(alarm[3], alarm[2], alarm[1], alarm[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(0.2)
        time.sleep(0.2)
        pos += 1
        if pos == 3:
            if alarm[2] < dt0.month:
                year += 1
            if alarm[2] in [1, 3, 5, 7, 8, 10, 12]:
                upper_limit[3] = 31
            elif alarm[2] in [4, 6, 9, 11]:
                upper_limit[3] = 30
            else:
                if year % 4 == 0:
                    upper_limit = 29
                else:
                    upper_limit = 28
        if CM == globals.ClockMode:
            print_str16("{4:5} {0:02}/{1:02} {2:02}{3:02}".format(alarm[3], alarm[2], alarm[1], alarm[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(1)
    if CM == globals.ClockMode:
        msg = "{0:4}-{1:02}-{2:02} {3:02}:{4:02}".format(year, alarm[2], alarm[3], alarm[1], alarm[0])
        print(msg)
        dt = datetime.strptime(msg, "%Y-%m-%d %H:%M")
        # Activate the thread
        a = AlarmClock(dt)
        a.start()
        # print alarm set
        print_str16("Alarm set       ")
        write_display16()
        time.sleep(5)
        print_str16("Alarm {0:02}/{1:02} {2:02}{3:02}".format(alarm[3], alarm[2], alarm[1], alarm[0]))
        set_decimal_point16(13)
        write_display16()
        time.sleep(3)
        globals.ClockMode += 1
    # exit


def Timer():
    """ A countdown timer
    """
    clear_display16()

    # set the timer
    lower_limit = [0, 0, 0]
    upper_limit = [60, 60, 24]
    msg = ['Sec  ', 'Min  ', 'Hour ', 'Set  ']
    count = [0, 0, 0]  # sec, min, hour

    # get alarm time from the keys
    pos = 0
    print_str16("{3:5}{0:02}h{1:02}m{2:02}000".format(count[2], count[1], count[0], msg[0]))
    set_decimal_point16(12)
    write_display16()

    CM = globals.ClockMode  # detect change in MODE
    while pos < 3 and CM == globals.ClockMode:
        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):
            if globals.B[2].is_pressed:
                count[pos] -= 1
            if globals.B[4].is_pressed:
                count[pos] += 1
            if count[pos] < lower_limit[pos]:
                count[pos] = upper_limit[pos] - 1
            if count[pos] >= upper_limit[pos]:
                count[pos] = lower_limit[pos]
            print_str16("{3:5}{0:02}h{1:02}m{2:02}000".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(12)
            write_display16()
            time.sleep(0.2)
        time.sleep(0.2)
        pos += 1
        if CM == globals.ClockMode:  # timer set: display
            print_str16("{3:5}{0:02}h{1:02}m{2:02}000".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(12)
            write_display16()
            time.sleep(1)

    timer = count[0] + 60 * count[1] + 60 * 60 * count[2]  # seconds
    origTimer = timer
    zero = timedelta(seconds=0)
    mpc.clear()
    while CM == globals.ClockMode:
        print_str16('{:>16}'.format(td_format_milliseconds(timedelta(seconds=timer))), True)
        set_decimal_point16(12)
        write_display16()

        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):  # Wait for GO
            if globals.B[4].is_pressed and CM == globals.ClockMode:
                timer = origTimer
            time.sleep(0.1)

        t0 = datetime.now() + timedelta(microseconds=timer * 1000000)
        dt = t0 - t0
        finish = False
        # Running: STOP and MODE interrupt
        while (not globals.B[4].is_pressed) and (CM == globals.ClockMode) and not finish:
            t1 = datetime.now()
            dt = t0 - t1
            if dt <= zero:
                finish = True
                dt = timedelta(seconds=0)
            print_str16('{:>16}'.format(td_format_milliseconds(dt)), True)
            set_decimal_point16(12)
            write_display16()
            time.sleep(0.001)

        if (CM == globals.ClockMode) and not finish:  # STOP was pressed, wait for GO
            timer = dt.microseconds / 1000000 + dt.seconds
        else:
            print_str16('{:>16}'.format(td_format_milliseconds(dt)), True)
            set_decimal_point16(12)
            write_display16()
            time.sleep(0.2)
            # if finish: beep timer finish
            if globals.AlarmTone == 0:
                globals.BUZZ.beep(0.1, 0.05, 5)
            else:
                mpc.clear()
                mpc.alarm(globals.AlarmTone)

            while (not globals.B[1].is_pressed) and (CM == globals.ClockMode):  # Waiting for RESET or MODE change
                time.sleep(0.2)

            mpc.stop()
            timer = origTimer
            # if RESET, restart the loop
            # if MODE changed, exit the loop and the thread will redirect


def WorldClock():
    """ A world clock
        Timezones are read from a parameter file, see globals and the main module
    """
    CM = globals.ClockMode
    pos = 0
    while CM == globals.ClockMode and globals.running.is_set():
        tzi = ICUtzinfo.getInstance(globals.TimeZones[pos][0])  # ICU time zone instance, to set the clock
        msg = globals.TimeZones[pos][1]  # display name

        d0 = datetime.now(tzi)
        DST = d0.dst().total_seconds()  # gets the daylight savings time difference in seconds
        if DST == 0.0:
            daylightSavingsIndicator = ' '  # no DST
        else:
            daylightSavingsIndicator = "*"  # DST ongoing

        print_str16("{:8}{}{:7}".format(msg[:8], daylightSavingsIndicator, d0.strftime("%d %H%M")))
        set_decimal_point16(13)
        write_display16()

        if globals.B[1].is_pressed:
            # previous tz
            pos -= 1
            if pos < 0:
                pos = len(globals.TimeZones) - 1
            # time.sleep(0.2)
        if globals.B[5].is_pressed:
            # next tz
            pos += 1
            if pos >= len(globals.TimeZones):
                pos = 0
            # time.sleep(0.2)
        time.sleep(0.2)


def ChessClock():
    """ A clock for playing chess
        Game time is set for both players, B[2] and B[4] move count up.down, B[3] when ready
        Press B[1] or B[5] to start a countdown, and alternate between players
    """

    # Indicate sides
    white_left = True
    CM = globals.ClockMode
    while (not globals.B[3].is_pressed) and CM == globals.ClockMode:
        if globals.B[1].is_pressed or globals.B[5].is_pressed:
            white_left = not white_left
        if white_left:
            print_str16("Whites    Blacks")
        else:
            print_str16("Blacks    Whites")
        write_display16()
        time.sleep(0.2)

    if white_left:
        white_button = 1
        black_button = 5
    else:
        white_button = 5
        black_button = 1

    lower_limit = [0, 0, 0]
    upper_limit = [60, 60, 10]

    # set playing time: Whites

    msg = ['Whites s  ', 'Whites m  ', 'Whites h  ', 'Set       ']
    count = [0, 0, 0]  # sec, min, hour

    pos = 0
    print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
    set_decimal_point16(13)
    write_display16()

    while pos < 3 and CM == globals.ClockMode:
        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):
            if globals.B[2].is_pressed:
                count[pos] -= 1
            if globals.B[4].is_pressed:
                count[pos] += 1
            if count[pos] < lower_limit[pos]:
                count[pos] = upper_limit[pos] - 1
            if count[pos] >= upper_limit[pos]:
                count[pos] = lower_limit[pos]
            print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(0.2)
        time.sleep(0.2)
        pos += 1
        if CM == globals.ClockMode:  # timer set: display
            print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(1)

    tw = timedelta(seconds=count[0] + 60 * count[1] + 60 * 60 * count[2])  # seconds

    msg = ['Blacks s  ', 'Blacks m  ', 'Blacks h  ', 'Set       ']
    # keep the count vector as a default for the blacks, or set count = [0, 0, 0]  # sec, min, hour

    # set playing time: Blacks
    pos = 0
    print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
    set_decimal_point16(13)
    write_display16()

    while pos < 3 and CM == globals.ClockMode:
        while (not globals.B[3].is_pressed) and (CM == globals.ClockMode):
            if globals.B[2].is_pressed:
                count[pos] -= 1
            if globals.B[4].is_pressed:
                count[pos] += 1
            if count[pos] < lower_limit[pos]:
                count[pos] = upper_limit[pos] - 1
            if count[pos] >= upper_limit[pos]:
                count[pos] = lower_limit[pos]
            print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(0.2)
        time.sleep(0.2)
        pos += 1
        if CM == globals.ClockMode:  # timer set: display
            print_str16("{3:10}{0:1}h{1:02}{2:02}".format(count[2], count[1], count[0], msg[pos]))
            set_decimal_point16(13)
            write_display16()
            time.sleep(1)

    tb = timedelta(seconds=count[0] + 60 * count[1] + 60 * 60 * count[2])  # seconds

    # wait for GO
    clear_display16()
    if white_left:
        msg = "{:>6} GO {:>6}".format(td_format_seconds_6(tw), td_format_seconds_6(tb))
    else:
        msg = "{:>6} GO {:>6}".format(td_format_seconds_6(tb), td_format_seconds_6(tw))
    print_str16(msg)
    set_decimal_point16(3)
    set_decimal_point16(13)
    write_display16()
    while not globals.B[3].is_pressed and CM == globals.ClockMode:
        time.sleep(0.2)

    # Running, Whites first
    zero = timedelta(seconds=0)
    finish = False
    while not finish and CM == globals.ClockMode:

        t0 = datetime.now()
        # Whites clock running
        while not finish and not globals.B[white_button].is_pressed and CM == globals.ClockMode:
            t1 = datetime.now()
            dt = t1 - t0
            if tw - dt <= zero:
                finish = True
                globals.BUZZ.beep(0.1, 0.05, 5)
            if white_left:
                msg = "{:>6} WB {:>6}".format(td_format_seconds_6(tw - dt), td_format_seconds_6(tb))
            else:
                msg = "{:>6} BW {:>6}".format(td_format_seconds_6(tb), td_format_seconds_6(tw - dt))
            print_str16(msg)
            set_decimal_point16(3)
            set_decimal_point16(13)
            write_display16()
            time.sleep(0.2)
        tw -= dt

        if not finish:
            t0 = datetime.now()
            # Blacks clock running
            while not finish and not globals.B[black_button].is_pressed and CM == globals.ClockMode:
                t1 = datetime.now()
                dt = t1 - t0
                if tb - dt <= zero:
                    finish = True
                    globals.BUZZ.beep(0.1, 0.05, 5)
                if white_left:
                    msg = "{:>6} WB {:>6}".format(td_format_seconds_6(tw), td_format_seconds_6(tb - dt))
                else:
                    msg = "{:>6} BW {:>6}".format(td_format_seconds_6(tb - dt), td_format_seconds_6(tw))
                print_str16(msg)
                set_decimal_point16(3)
                set_decimal_point16(13)
                write_display16()
                time.sleep(0.2)
            tb -= dt
    if finish:
        while not globals.B[3].is_pressed and CM == globals.ClockMode:  # wait for GO or MODE
            time.sleep(0.2)


class AlarmClock(threading.Thread):
    """ Operates an alarm for the provided time
        alarmTime is a full datetime object
    """

    def __init__(self, alarmTime, alarmActive=True):
        threading.Thread.__init__(self)
        self.alarmTime = alarmTime
        self.alarmActive = alarmActive
        self.stop = False  # stop the thread if True
        print("Initializing alarm clock thread. Set to " + self.alarmTime.strftime("%Y-%m-%d %H:%M"))

    def toggleAlarm(self):
        self.alarmActive = not self.alarmActive

    def run(self):
        while not self.stop and globals.running.is_set():
            d0 = datetime.now()
            if (d0 >= self.alarmTime) and self.alarmActive:
                globals.display_override.set()
                print("Wake up time")  # sound alarm
                print_str16("Alarm Alarm " + self.alarmTime.strftime("%H%M"), override=True)
                set_decimal_point16(13, print_override=True)
                write_display16()
                if globals.AlarmTone == 0:
                    globals.BUZZ.beep(0.1, 0.05, 5)
                else:
                    mpc.clear()
                    mpc.alarm(globals.AlarmTone)
                CM = globals.ClockMode
                while not globals.B[3].is_pressed and CM == globals.ClockMode:
                    time.sleep(1)
                mpc.clear()
                globals.display_override.clear()
                self.stop = True
            if not self.stop:
                time.sleep(30)
        mpc.stop()
        mpc.clear()
        self.toggleAlarm()
