#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------
# Un simple bot que replica mensajes de Telegram.
# Presione Ctrl-C en la línea de comandos o envíe una señal al proceso para detener el bot.
# ------------------------------------------------------------------------------------------

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
import logging

# Activar logueo:
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Guarda tiempo para usar en funciones 'todos' y 'nojodan':
tiempo_final = None


def frase_al_azar(frases):
    '''Función que elije una frase al azar de una lista pasada y la devuelve a la función invocante.'''
    import random

    pos = random.randint(0, len(frases)-1)
    return frases[pos]


def ayuda(bot, update):
    '''Mandar un mensaje cuando el comando /ayuda es enviado.'''
    from frases import mensaje_ayuda
    update.message.reply_text(mensaje_ayuda, quote=False)


def clima(bot, update):
    '''Manda un mensaje con los datos del clima de CABA.'''
    import clima
    import datetime as dt
    datos = clima.ahora()

    temp = str(datos['temp']) + '°'
    minima = str(datos['temp_min']) + '°'
    maxima = str(datos['temp_max']) + '°'
    humedad = str(datos['humedad']) + '%'
    viento = str(round((datos['viento'] * 3.6), 2)) + ' km/h'  # Pasando de m/s a km/h (y después casteando a string).
    descripcion = str(datos['descripcion'])

    hora = dt.datetime.fromtimestamp(datos['ts_ultimo'])
    dia_o_noche = str(datos['dia_o_noche'])
    hora = str(dt.datetime.now().hour) + ':'
    minutos = dt.datetime.now().minute
    if minutos < 10:
        minutos =  '0' + str(minutos) 
    else:
        minutos = str(minutos)
    hora += minutos

    if datos:
        update.message.reply_text('[El clima en Ｃ Ａ Ｂ Ａ]\n\n' +
                                '  - {0}\n'.format(descripcion) +
                                '  - Temp: {0}\n  (Min: {1} / Máx: {2})\n'.format(temp, minima, maxima) +
                                '  - Humedad: {0}\n'.format(humedad) +
                                '  - Viento: {0}'.format(viento),
                                quote=False)
    else:
        update.message.reply_text('Sorry, no pude conseguir los datos del clima. :(', quote=False)


def dilotuyo(bot, update):
    '''Manda un mensaje random al usuario/chat grupal.'''
    from frases import frases

    update.message.reply_text(frase_al_azar(frases), quote=False)


def todos(bot, update, args):
    '''Mandar un mensaje a todos los usuarios cuando el comando /todos es enviado.'''

    import time
    tiempo_actual = round(time.time())

    global tiempo_final

    # Comprobamos si hay un tiempo final fijado y si el tiempo actual no lo sobrepasó:
    if tiempo_final != None:
        if tiempo_actual >= tiempo_final:
            tiempo_final = None

    # Si no hay un tiempo final fijado, podemos usar la función:
    if tiempo_final == None:
        from frases import usuarios
        mensaje_user = ' '.join(args)
        update.message.reply_text("<b>{0}</b>\n\n{1}".format(usuarios, mensaje_user),
                                  quote=False, parse_mode=ParseMode.HTML)
    
    # En caso de si haberlo, lo advertimos:
    else:
        from frases import mensajes_no_jodas

        tiempo_restante = round(tiempo_final-tiempo_actual)
        unidad = "segundos"

        if tiempo_restante >= 60 and tiempo_restante < 3600:
            tiempo_restante = round(tiempo_restante / 60)
            unidad = "minutos"

        update.message.reply_text("Faltan como {0} {1} para poder usar <b>/todos</b> de nuevo.".format(str(tiempo_restante), unidad),
                                  quote=False, parse_mode=ParseMode.HTML)
        update.message.reply_text(frase_al_azar(mensajes_no_jodas), quote=False)


def nojodan(bot, update, args):
    '''Cancela la función '/todos' por X tiempo y manda mensaje avisando dicha cancelación.'''
    
    import time
    from frases import mensajes_no_jodas, unidades

    tiempo_actual = round(time.time())

    global tiempo_final

    # En casi de haber un tiempo establecido...
    if tiempo_final != None: 
        if tiempo_actual < tiempo_final:

            tiempo_restante = round(tiempo_final-tiempo_actual)
            unidad = "segundos"

            if tiempo_restante >= 60 and tiempo_restante < 3600:
                tiempo_restante = round(tiempo_restante / 60)
                unidad = "minutos"

            update.message.reply_text("No se puede usar de nuevo hasta que no pase el tiempo anteriormente fijado (falta {0} {1}).".format(str(tiempo_restante), unidad),
                                      quote=False, parse_mode=ParseMode.HTML)
            update.message.reply_text(frase_al_azar(mensajes_no_jodas), quote=False)

    # En caso de NO haber un tiempo establecido...
    else:
        tiempo = 0
        unidad = ""

        if len(args) > 0:
            for valor in args:
                valor = valor.lower()

                # Si el argumento es decimal lo casteamos a un entero:
                if valor.isdecimal() and tiempo == 0:
                    tiempo = int(valor)

                # Si el argumento es una unidad de medida reconocido:
                elif valor in unidades:
                    unidad = valor
                    tiempo_en_seg = unidades[valor]

                # En cualquier otro caso, avisamos y seteamos valores por defecto:
                else: 
                    update.message.reply_text("No entendí el valor y/o la unidad que me pasaste, asi que ahora te jodes y pongo lo que se me canta.",
                                              quote=False, parse_mode=ParseMode.HTML)

            
            # Si no se reconoció un valor, se fija a los valores por defecto:
            if unidad == "" or tiempo == 0:
                tiempo = 10
                unidad = "minutos"
                tiempo_en_seg = tiempo * unidades[unidad]

            # En caso de haberse reconocido los argumentos pasados...
            else:
                tiempo_en_seg = tiempo * unidades[unidad]

        # Si no se pasó argumentos, se fija a los valores por defecto:
        else:
            tiempo = 10
            unidad = "minutos"
            tiempo_en_seg = tiempo * unidades[unidad]

        # Si el tiempo es menor a 10 segundos, se retorna:
        if tiempo_en_seg < 10:
            update.message.reply_text("<b>¿¡{0} {1}!?</b> Dale bola, pasame un tiempo razonable.".format(str(tiempo), unidad),
                                      quote=False, parse_mode=ParseMode.HTML)
            return

        # Si el tiempo se excede de un día, lo limitamos entonces a 1 hora:
        if tiempo_en_seg > 3600:
            update.message.reply_text("No lo voy a poner en {0} {1} ni en pedo, olvidate.".format(str(tiempo), unidad),
                                      quote=False, parse_mode=ParseMode.HTML)
            tiempo = 1
            unidad = "hora"
            tiempo_en_seg = tiempo * unidades[unidad]

        # Seteando tiempo final:
        tiempo_final = tiempo_actual + tiempo_en_seg
        update.message.reply_text("La función <b>/todos</b> fue desactivada por {0} {1}.".format(str(tiempo), unidad),
                                  quote=False, parse_mode=ParseMode.HTML)


def error(bot, update, error):
    '''Loguea errores causados por Update's.'''
    logger.warning("Update '%s' caused error '%s'", update, error)


def main(token):
    '''Inicia el bot.'''

    # Crea EventHandler y pasa el token de nuestro bot:
    updater = Updater(token)

    # Obtiene dispatcher para poder registrar los handlers a ser usados:
    dp = updater.dispatcher

    # Handlers:
    dp.add_handler(CommandHandler('ayuda', ayuda))
    dp.add_handler(CommandHandler('clima', clima))
    dp.add_handler(CommandHandler('dilotuyo', dilotuyo))
    dp.add_handler(CommandHandler('todos', todos, pass_args=True))
    dp.add_handler(CommandHandler('nojodan', nojodan, pass_args=True))

    # Loguea todos los errores:
    dp.add_error_handler(error)

    # Inicia el bot:
    updater.start_polling()

    # Ejecuta el bot hasta que se pulse Ctrl-C:
    updater.idle()


if __name__ == '__main__':
    
    import sys
    token = sys.argv[1]

    if token != None:
        main(token)
    else:
        print("\nError: no se pasó el token necesario para ejecutar el script.")
        print("Abortando.\n")
