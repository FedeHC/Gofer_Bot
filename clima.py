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

        descripcion = traducir(json['weather'][0]['description'], clima['dia_o_noche'])
        clima.update({'descripcion': descripcion})

        return clima

    else:
        return None


def traducir(descripcion, dia_o_noche):
        '''Función para traducir una descripción del clima recibido en inglés.'''

        if descripcion == 'clear sky':
            if dia_o_noche == 'dia':
                icono = '☀️'
            else:
                icono = '🌙'
            descripcion = 'Está despejado ({0}),\nideal para salir de la cueva.'.format(icono)

        elif 'clouds' in descripcion and descripcion != 'overcast clouds':
            if dia_o_noche == 'dia':
                icono = '🌤'
            else:
                icono = '☁️🌙☁️'
            descripcion = 'Hay algunas nubes ({0}),\npero todavía sirve (?).'.format(icono)

        elif descripcion == 'overcast clouds':
            icono = '☁️'
            descripcion = 'Está re nublado ({0}),\ncomo para ver Netflix.'.format(icono)

        elif 'drizzle' in descripcion or 'rain' in descripcion:
            icono = '🌧'
            descripcion = 'Está lloviendo ({0}),\ny yo sin lancha, qué picardía.'.format(icono)

        elif descripcion == 'thunderstorm':
            icono = '⛈'
            descripcion = 'Alta tormenta ({0}),\nquedate ahí, NO SALGAS'.format(icono)

        elif descripcion == 'snow':
            icono = '❄️'
            descripcion = 'Está nevando ({0}),\nsalí a hacer el muñeco de nieve YA.'.format(icono)

        elif descripcion == 'mist' or descripcion == 'fog':
            icono = '🌫'
            descripcion = 'No veo un carajo ({0}),\n debe haber alta neblina.'.format(icono)

        else:
            descripcion = 'No sé nada, no tengo datos, aiuda plis. :S'

        return descripcion
