#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
- Un simple bot que replica mensajes de Telegram..
- Presione Ctrl-C en la línea de comandos o envíe una señal al proceso para detener el bot..
"""

from telegram.ext import Updater, CommandHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def frase_al_azar():
    """Se elije una frase al azar y se devuelve a la función invocante."""
    import random
    from frases import frases
    pos = random.randint(0, len(frases)-1)
    return frases[pos]


# Define algunos manejadores de comandos. Estos usualmente toman los dos argumentos, bot y update.
# Los error handlers también reciben el objeto TelegramError al surgir error.
def ayuda(bot, update):
    """Mandar un mensaje cuando el comando /ayuda es enviado."""
    from frases import mensaje_ayuda
    update.message.reply_text(mensaje_ayuda, quote=False)

def clima(bot, update):
    """Manda un mensaje con los datos del clima de CABA."""
    import clima
    import datetime as dt
    datos = clima.ahora()

    temp = str(datos['temp']) + "°"
    minima = str(datos['temp_min']) + "°"
    maxima = str(datos['temp_max']) + "°"
    humedad = str(datos['humedad']) + "%"
    hora = dt.datetime.fromtimestamp(datos['ts_ultimo'])

    # dia_o_noche = clima["de_dia"]
    hora = str(dt.datetime.now().hour) + ":"
    minutos = dt.datetime.now().minute
    if minutos < 10:
        minutos =  "0" + str(minutos) 
    else:
        minutos = str(minutos)
    
    hora += minutos

    if datos:
        update.message.reply_text("El clima ahora a las {0} hs. en CABA:\n".format(hora) +
                                "- Temp: {0} (Min: {1} / Max: {2})\n".format(temp, minima, maxima) +
                                "- Humedad: {0}".format(humedad),
                                quote=False)
    else:
        update.message.reply_text("Sorry, no pude conseguir los datos del clima. :(",
                                 quote=False)


def dilotuyo(bot, update):
    """Manda un mensaje random al usuario."""
    update.message.reply_text(frase_al_azar(), quote=False)


def error(bot, update, error):
    """Loguea errores causados por Update's."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Inicia el bot."""
    # Crea EventHandler y pasa el token de tu bot:
    updater = Updater("613009817:AAHQhu7ggAUPJnhJdfWmHsHijVC1zrGGguU")

    # Obtiene dispatcher para poder registrar los handlers a usar:
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("ayuda", ayuda))
    dp.add_handler(CommandHandler("clima", clima))
    dp.add_handler(CommandHandler("dilotuyo", dilotuyo))

    # Loguea todos los errores:
    dp.add_error_handler(error)

    # Inicia el bot:
    updater.start_polling()

    # Ejecuta el bot hasta que se pulse Ctrl-C o hasta que el proceso reciba SIGINT,
    # SIGTERM o SIGABRT. Esto debería ser usado la mayor parte del tiempo, ya que
    # start_polling() no bloquea y detiene el bot sin problemas:
    updater.idle()


if __name__ == '__main__':
    main()

    """Inicia el bot."""
    # Crea EventHandler y pasa el token de tu bot:
    updater = Updater("613009817:AAHQhu7ggAUPJnhJdfWmHsHijVC1zrGGguU")

    # Obtiene dispatcher para poder registrar los handlers a usar:
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("arranca", arranca))
    dp.add_handler(CommandHandler("ayuda", ayuda))
    dp.add_handler(CommandHandler("dilotuyo", dilotuyo))

    # Loguea todos los errores:
    dp.add_error_handler(error)

    # Inicia el bot:
    updater.start_polling()

    # Ejecuta el bot hasta que se pulse Ctrl-C o hasta que el proceso reciba SIGINT,
    # SIGTERM o SIGABRT. Esto debería ser usado la mayor parte del tiempo, ya que
    # start_polling() no bloquea y detiene el bot sin problemas:
    updater.idle()


if __name__ == '__main__':
    main()
