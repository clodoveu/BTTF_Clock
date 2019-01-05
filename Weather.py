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

def current_weather(city = 'SBBH'):
    """ Imprime no display16 o tempo atual segundo o CPTEC/INPE
        Parametro city: codigo de aeroporto - default: SBBH, codigo do aeroporto de Belo Horizonte
    """
    clear_display16()

    try:
        td = ScrollDisplayThread(unidecode.unidecode(CPTEC.cptec_current_weather('SBBH')), 16)
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

def weather_forecast(city = '222', days = 2):
    """ Imprime no display16 o tempo atual segundo o CPTEC/INPE
        Parametro city: codigo da cidade - default: 222', codigo de Belo Horizonte
        Parametro days: numero de dias de previsao a apresentar, 1-4. Default: 2 dias
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

