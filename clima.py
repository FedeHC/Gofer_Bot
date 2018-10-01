#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Script para sacar datos del clima desde API de OpenWeatherMap.org.
# -------------------------------------------------------------------

def ahora():
    '''Función que devuelve diccionario con datos del clima, obtenidos desde API de OpenWeatherMap.org.'''
    import json, requests
    import datetime as dt

    # Url:
    tipo_pronostico = 'weather'
    ciudad = 'Ciudad Autónoma de Buenos Aires'
    unidad = 'metric'
    idioma = 'en'
    api_key = '9207292b2ee0882a607f4058f6fb9da3'
    url = 'http://api.openweathermap.org/data/2.5/{0}?q={1}&units={2}&lang={3}&appid={4}'.format(
        tipo_pronostico, ciudad, unidad ,idioma, api_key)

    # Request:
    respuesta = requests.get(url)

    # Si salió bien el request:
    if(respuesta.status_code == requests.codes.ok):

        # Json:
        json = json.loads(respuesta.text)

        # Diccionario c/los datos necesarios:
        clima = { 'ts_ultimo': json['dt'],
                'ts_amanece': json['sys']['sunrise'],
                'ts_anochece': json['sys']['sunset'],
                'temp': json['main']['temp'],
                'temp_min': json['main']['temp_min'],
                'temp_max': json['main']['temp_max'],
                'humedad': json['main']['humidity'],
                'viento': json['wind']['speed'],
                'ciudad': json['name'] }

        ahora = clima['ts_ultimo']
        amanece = clima['ts_amanece']
        anochece = clima['ts_anochece']

        if ahora > amanece and ahora < anochece:
            clima.update({'dia_o_noche': 'dia'})
        else:
            clima.update({'dia_o_noche': 'noche'})

        descripcion, icono = traducir(json['weather'][0]['description'], clima['dia_o_noche'])
        clima.update({'descripcion': descripcion})
        clima.update({'icono': icono})

        return clima

    else:
        return None


def traducir(descripcion, dia_o_noche):
        '''Función para traducir una descripción del clima recibido en inglés.'''

        if descripcion == 'clear sky':
            descripcion = 'Está despejado, como para salir.'
            if dia_o_noche == 'dia':
                icono = '☀️'
            else:
                icono = '🌙'

        elif 'clouds' in descripcion and descripcion != 'overcast clouds':
            descripcion = 'Hay algunas nubes me parece..'
            if dia_o_noche == 'dia':
                icono = '🌤'
            else:
                icono = '☁️🌙☁️'

        elif descripcion == 'overcast clouds':
            descripcion = 'Está nubladito nubladón (qué cagada).'
            icono = '☁️'

        elif 'drizzle' in descripcion or 'rain' in descripcion:
            descripcion = 'Está lloviendo, lpmqlp.'
            icono = '🌧'

        elif descripcion == 'thunderstorm':
            descripcion = 'Hay alta tormenta, NI SALGAS.'
            icono = '⛈'

        elif descripcion == 'snow':
            descripcion = 'Nevandooooooooooo a fuuuull!'
            icono = '❄️'

        elif descripcion == 'mist' or descripcion == 'fog':
            descripcion = 'No veo nada, asi que hay neblina.'
            icono = '🌫'

        else:
            descripcion = 'No sé nada, no tengo datos, aiuda. :S'
            icono = '❓'

        return descripcion, icono
