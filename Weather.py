# !/usr/bin/python3
#
# Back to the Future Clock
# Version 4
#
# CADJ 28/12/2018
#
# Weather display functions
#

import CPTEC
from Display import *
import globals
import unidecode
from mpc import *


def current_weather(city='SBBH'):
    """ Prints current weather to display16 according to CPTEC/INPE
        Parameter city: CPTEC airport code - default: SBBH, Belo Horizonte's airport
    """
    clear_display16()

    try:
        td = ScrollDisplayThread(unidecode.unidecode(CPTEC.cptec_current_weather(city)), 16)
        td.start()
        # signal.pause()
    except (KeyboardInterrupt, SystemExit):
        mpc.stop()
        mpc.clear()
        clear_display16()
        sys.exit()

    CM = globals.ClockMode
    while CM == globals.ClockMode:  # wait for MODE change
        time.sleep(1)

    td.stop = True  # end the scrolling display


def weather_forecast(city='222', days=2):
    """ Displays current weather forecast according to CPTEC/INPE
        Parameter city: city code - default: 222, for Belo Horizonte
        Parameter days: number of forecast days to display, 1 to 4. Default: 2
    """
    clear_display16()

    forecast = CPTEC.cptec_forecast(city)  # list
    msg = 'Previsao '
    for i in range(days):
        msg += forecast[i] + ' '

    try:
        td = ScrollDisplayThread(msg, 16)
        td.start()
        # signal.pause()
    except KeyboardInterrupt:
        mpc.stop()
        mpc.clear()
        clear_display16()
        sys.exit()

    CM = globals.ClockMode
    while CM == globals.ClockMode:  # wait for MODE change
        time.sleep(1)

    td.stop = True  # end the scrolling display
