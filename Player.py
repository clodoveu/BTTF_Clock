# !/usr/bin/python3
#
# Back to the Future Clock
# MP3 player functions
# Version 4.1
# Change to MPD/MPC
#
# CADJ 28/12/2018
#
#

# OS and low-level
import time
import signal
import subprocess

import datetime
from datetime import datetime
import re

# Local modules
import globals
import mpc
from Display import *
from Buttons import *

# Decoding Unicode to ASCII preserving the closest form of accented letters
import unidecode

# Working Parameters
MP3_pause_state = False


def VolUp():
    """ Increases the volume by 5%
    """
    globals.MP3_Vol += 5
    if globals.MP3_Vol > 100:
        globals.MP3_Vol = 100
    print("Vol+ {}".format(int(globals.MP3_Vol)))
    mpc.vol(globals.MP3_Vol)


def VolDown():
    """ Decreases the volume by 5%
    """
    globals.MP3_Vol -= 5
    if globals.MP3_Vol < 0:
        globals.MP3_Vol = 0
    print("Vol- {}".format(int(globals.MP3_Vol)))
    mpc.vol(globals.MP3_Vol)


def Pause():
    """ Toggles Play and Pause
    """
    global MP3_pause_state
    if MP3_pause_state == True:
        MP3_pause_state = False
        mpc.pause()
    else:
        MP3_pause_state = True
        mpc.play()


def Next():
    """ Moves to the next song in the playlist
        or to the next radio station
    """
    mpc.next()


def Previous():
    """ Goes back to the previous song
        or to the previous radio station
    """
    mpc.prev()


def initMP3():
    """ Initialize the MP3 player
    """
    mpc.stop()  # stop what's playing
    mpc.clear()  # clear any existing playlists
    mpc.repeat(True)  # repeat mode so the play cycles at the end of the playlist


def init_MP3_playlist(mode=0):
    """ Build a playlist:
        mode = 0 -> playlist will be formed using the MP3filter from the MP3 folder
        mode = 1 -> playlist formed from the list of internet radio stations on file
        MP3 folder specified externally to mpd, using /etc/mpd.conf
    """
    if mode == 0:
        if globals.MP3_Filter == '':
            mpc.fill_playlist()  # create a playlist from all songs in the Music folder
        else:  # apply multi-clause globals.MP3_Filter
            for clause in re.split('\|', globals.MP3_Filter):  # split list of filters, vertical bar separator
                mpc.filter(clause.strip())  # .filter function searches and adds, so the clauses are now conjunctive
        mpc.shuffle()  # Shuffle playlist
    else:
        mpc.fill_radiolist()  # create a playlist from the radio stations file
    mpc.vol(globals.MP3_Vol)  # Set default volume


def getNowPlayingString():
    """ Gets the description of what is playing from the "mpc current" command
    """
    msg = unidecode.unidecode(mpc.current())
    return msg


def play_mp3(mode=0):
    """ Play the next MP3 file in the playlist (mode 0), or the next radio station (mode 1)
    """
    globals.B[1].when_pressed = Previous
    globals.B[2].when_pressed = VolDown
    globals.B[3].when_pressed = Pause
    globals.B[4].when_pressed = VolUp
    globals.B[5].when_pressed = Next

    mpc.play()
    msg = getNowPlayingString()

    # Use 12 leftmost digits to scroll title and artist
    # The remaining 4 digits display the playing time
    # For internet radio, use the 16 characters
    if mode == 0:
        width = 12
    else:
        width = 16
    try:
        td = ScrollDisplayThread(msg, width)
        td.start()
        # signal.pause()
    except (KeyboardInterrupt, SystemExit):
        mpc.stop()
        mpc.clear()
        clear_display16()
        sys.exit()

    CM = globals.ClockMode
    msg_ant = msg
    d0 = datetime.now()
    while CM == globals.ClockMode:
        msg = getNowPlayingString()
        if mode == 0:  # MP3 with a running clock
            dt = datetime.now() - d0
            minute, second = divmod(int(dt.total_seconds()), 60)
            tstr = "{0:02d}{1:02d}".format(minute, second)
            print_time(tstr)
        if msg != msg_ant:
            td.msg = msg
            msg_ant = msg
            d0 = datetime.now()
        time.sleep(1)
    td.stop = True  # Stop the thread for the scrolling display
    mpc.stop()  # stop playing
    mpc.clear()  # clear existing playlists
    clear_display16()
