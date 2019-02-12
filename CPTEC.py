# !/usr/bin/python3
#
#
# CADJ 01/01/2019
# Weather functions based on INPE/CPTEC services
#
#
import urllib.request
import xmltodict

siglas_tempo = {
    'c': "chuva",
    'ch': "chuvoso",
    'ci': "chuvas isoladas",
    'cl': "ceu claro",
    'cm': "chuva pela manha",
    'cn': "chuva a noite",
    'ct': "chuva a tarde",
    'cv': "chuvisco",
    'e': "encoberto",
    'ec': "encoberto com chuvas isoladas",
    'g': "geada",
    'in': "instavel",
    'n': "nublado",
    'ncm': "nublado possib chuva pela manha",
    'ncn': "nublado possib chuva a noite",
    'nct': "nublado possib chuva a tarde",
    'nd': "nao definido",
    'ne': "neve",
    'np': "nublado e pancadas de chuva",
    'npm': "nublado com pancadas pela manha",
    'npn': "nublado com pancadas a noite",
    'npp': "nublado com possib chuva",
    'npt': "nublado com pancadas a tarde",
    'nv': "nevoeiro",
    'pc': "pancadas de chuva",
    'pcm': "possibilidade de chuva pela manha",
    'pcn': "possibilidade de chuva a noite",
    'pct': "possibilidade de chuva a tarde",
    'pm': "pancadas de chuva pela manha",
    'pn': "parcialmente nublado",
    'pnt': "pancadas de chuva a noite",
    'pp': "possib pancadas de chuva",
    'ppm': "possib pancadas pela manha",
    'ppn': "possib pancadas a noite",
    'ppt': "possib pancadas a tarde",
    'ps': "predominio de sol",
    'psc': "possibilidade de chuva",
    'pt': "pancadas de chuva a tarde",
    't': "tempestade",
    'vn': "variacao de nebulosidade"
}


def cptec_current_weather(airport_code):
    """ Retorna um string com as condicoes atuais do tempo, segundo o CPTEC/INPE
        Parametro: codigo de aeroporto
        Fonte: http://servicos.cptec.inpe.br/XML/
        Servico: http://servicos.cptec.inpe.br/XML/estacao/SBBH/condicoesAtuais.xml
    """
    CPTEC_ATUAL_URL = 'http://servicos.cptec.inpe.br/XML/estacao/' + airport_code + '/condicoesAtuais.xml'
    try:
        xml = urllib.request.urlopen(CPTEC_ATUAL_URL)
    except:
        return "Current Weather: Error "

    xml_string_atual = xml.read()
    xml.close()

    weather_dict = xmltodict.parse(xml_string_atual)
    return "Temp {}C {} Umid {}% ".format(int(weather_dict['metar']['temperatura']),
                                          weather_dict['metar']['tempo_desc'],
                                          int(weather_dict['metar']['umidade']))


def cptec_forecast(city_code):
    """ Retorna um string com a previsao do tempo para os proximos 4 dias, inclusive o atual, como um vetor de 4 strings
        Parametro: codigo de cidade
        Fonte: http://servicos.cptec.inpe.br/XML/
        Servico: http://servicos.cptec.inpe.br/XML/cidade/codigo_da_localidade/previsao.xml
        Busca do codigo de cidades a partir do nome
        disponivel em http://servicos.cptec.inpe.br/XML/listaCidades?city=sao paulo
    """
    CPTEC_PREV4_URL = 'http://servicos.cptec.inpe.br/XML/cidade/' + city_code + '/previsao.xml'
    try:
        xml = urllib.request.urlopen(CPTEC_PREV4_URL)
    except:
        return "Weather Forecast: Error "

    xml_string_prev4 = xml.read()
    xml.close()

    weather_dict2 = xmltodict.parse(xml_string_prev4)
    dia = []
    for prev in weather_dict2['cidade']['previsao']:
        msg = ''
        y, m, d = prev['dia'].split('-')
        msg += "{:2}/{:2} ".format(d, m)
        msg += siglas_tempo[prev['tempo']]
        msg += " min " + prev['minima']
        msg += " max " + prev['maxima']
        msg += " UV {}".format(int(float(prev['iuv'])))
        dia.append(msg)
    return dia
