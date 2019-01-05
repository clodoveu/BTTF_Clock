# !/usr/bin/python3
#
# Back to the Future Clock
# Media player module
# MPD / MPC version
# Version 4
#
# CADJ 30/12/2018
#
#

import subprocess
from subprocess import call
import glob
import globals


def play(index=None):
    """ Play command
    """
    if index is None:
        call('mpc -q play', shell=True)
    else:
        call('mpc -q play {}'.format(index), shell=True)


def clear():
    """ Clear the playlist
    """
    call('mpc -q clear', shell=True)


def stop():
    """ Stops play
    """
    call('mpc -q stop', shell=True)


def next():
    """ Moves to the next song/station in the playlist
    """
    call('mpc -q next', shell=True)


def prev():
    """ Moves to the previous song/station in the playlist
    """
    call('mpc -q prev', shell=True)


def add(filename):
    """ Adds a song/station to the playlist
    """
    call('mpc -q add ' + filename, shell=True)


def insert(filename):
    """ Inserts a song/station in the current position of the playlist
    """
    call('mpc -q insert ' + filename, shell=True)


def current():
    """ Gets info on the currently playing file/station
    """
    result = subprocess.check_output(['mpc', 'current'])
    return result.decode('utf-8')


def shuffle():
    """ Shuffles the playlist
    """
    call('mpc -q shuffle', shell=True)


def pause():
    """ Pauses play
    """
    call('mpc -q pause', shell=True)


def status():
    """ Gets the status of MPC/MPD
    """
    result = []
    for line in subprocess.check_output(['mpc', 'status'], shell=True).decode('utf-8').split('\n'):
        result.append(line)
    return result


def repeat(param=None):
    """ Toggles the repeat play setting
        With no argument, toggles current setting
        Argument = True or False sets repeat to on or off
    """
    if param is None:
        p = ''
    elif param:
        p = 'on'
    else:
        p = 'off'
    call('mpc -q repeat {}'.format(p), shell=True)


def playlist_filter(f):
    """ Creates a filtered playlist using f as search string for mpc search
        Examples:  "artist Queen"
                   "title Stairway"
        All found results are added to the playlist
        Playlist should be cleared beforehand if only the results found are to be included,
        else subsequent filters add to the playlist
    """
    call('mpc search ' + f + ' | mpc add', shell=True)


def fill_playlist():
    """ Fill the playlist with the current contents of the Music folder
    """
    call('mpc -q ls | mpc add', shell=True)


def vol(v=50):
    """ Sets the volume
    """
    call('mpc -q volume {}'.format(v), shell=True)


def alarm(soundType=1):
    """ Plays an alarm
        type indicates the ringtone type
    """
    repeat(False)
    clear()
    n = 0
    for mp3file in glob.iglob(globals.RingtonesSource + '**/*.mp3', recursive=True):
        add(mp3file)
        n += 1
    soundType = soundType % n + 1  # 1 to n
    play(soundType)


def fill_radiolist():
    """ Plays an alarm
        type indicates the ringtone type
    """
    repeat(False)
    clear()
    try:
        # create the playlist from the radio stations list file
        with open(globals.RadioSource + globals.RadioList, 'r') as f:
            for line in f:
                if line[0] != '#':
                    station = line.split(',')[0]
                    add(station)
    except EnvironmentError:
        print("Radio stations file not found")
        add('http://sky1.torontocast.com:9085/stream')  # insert just one and hope
