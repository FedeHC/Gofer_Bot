#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------
# Un simple bot que replica mensajes de Telegram.
# Presione Ctrl-C en la línea de comandos o envíe una señal al proceso para detener el bot.
# ------------------------------------------------------------------------------------------


class Bot():
    '''Clase que contiene todos los métodos y handlers usados por Gofer_Bot.'''

    def __init__(self, api_bot, api_weather):
        from telegram.ext import Updater, CommandHandler
        import logging

        # Uso functools.partial para agregar una argumento extra a función handler:
        from functools import partial

        # Activar logueo:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Guarda tiempo para usar en funciones 'todos' y 'nojodan':
        self.tiempo_final = None

        # Dilotuyos por minuto:
        self.MAX_DILOTUYOS = 10
        self.LIMITE_SEGUNDOS = 300
        self.dilotuyos_mandados = 0
        self.tiempo = None
        self.mensaje_mostrado = False

        # Crea EventHandler y pasa el token de nuestro bot:
        updater = Updater(api_bot)

        # Obtiene dispatcher para poder registrar los handlers a ser usados:
        dp = updater.dispatcher

        # Handlers:
        dp.add_handler(CommandHandler('ayuda', self.ayuda))
        dp.add_handler(CommandHandler('clima', partial(self.clima, api=api_weather)))
        dp.add_handler(CommandHandler('dilotuyo', self.dilotuyo))
        dp.add_handler(CommandHandler('todos', self.todos, pass_args=True))
        dp.add_handler(CommandHandler('nojodan', self.nojodan, pass_args=True))

        # Loguea todos los errores:
        dp.add_error_handler(self.error)

        # Inicia el bot:
        updater.start_polling()

        # Ejecuta el bot hasta que se pulse Ctrl-C:
        updater.idle()


    def frase_al_azar(self, frases):
        '''Función que elije una frase al azar de una lista pasada y la devuelve a la función invocante.'''
        
        import random
        pos = random.randint(0, len(frases)-1)
        return frases[pos]


    def ayuda(self, bot, update):
        '''Mandar un mensaje cuando el comando /ayuda es enviado.'''

        from frases import mensaje_ayuda
        update.message.reply_text(mensaje_ayuda, quote=False)


    def clima(self, bot, update, api):
        '''Manda un mensaje con los datos del clima de CABA.'''

        import clima
        import datetime as dt
        datos = clima.ahora(api)

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


    def dilotuyo(self, bot, update):
        '''Manda un mensaje random al usuario/chat grupal.'''

        from telegram import ParseMode
        from frases import frases
        import time

        # Si hay un tiempo ya registrado...
        if self.tiempo:
            temp = round(time.time())

            # Si el último tiempo guardado fue hace 1 minuto o más, guardar nuevo tiempo:
            if temp >= self.tiempo + self.LIMITE_SEGUNDOS:
                self.tiempo = temp
                self.dilotuyos_mandados = 1
                self.mensaje_mostrado = False
                update.message.reply_text(self.frase_al_azar(frases), quote=False)

            # Si todavía no pasó el minuto...
            else:

                # Si se ha excedido el límite por minuto, avisar:
                if self.dilotuyos_mandados >= self.MAX_DILOTUYOS:
                    
                    # Mostrar mensaje de advertencia por única vez:
                    if not self.mensaje_mostrado:
                        self.mensaje_mostrado = True
                        update.message.reply_text("<i>Sorry, pero me parece que te estas pasando de límite con los dilotuyos.</i> 👮🏻",
                                                  quote=False, parse_mode=ParseMode.HTML)

                        limite_en_minutos = str(round(self.LIMITE_SEGUNDOS / 60))
                        update.message.reply_text("<i>Solo se admiten {0} dilotuyo\'s por cada {1} minutos, asi que hasta que no pase ese tiempo no te voy a mostrar un carajo.</i>".format(self.MAX_DILOTUYOS, limite_en_minutos),
                                                  quote=False, parse_mode=ParseMode.HTML)
                    
                    # Pasar de largo si ya se pasó el mensaje de advertencia.
                    else:
                        pass

                # Si no se ha excedido, sumar al contador y mostrar dilotuyo:
                else:
                    self.dilotuyos_mandados = self.dilotuyos_mandados + 1
                    update.message.reply_text(self.frase_al_azar(frases), quote=False)


        # En caso de no haber un tiempo seteado, crear uno, setear contador y mostrar dilotuyo:
        else:
            self.tiempo = round(time.time())
            self.dilotuyos_mandados = 1
            self.mensaje_mostrado = False
            update.message.reply_text(self.frase_al_azar(frases), quote=False)
       

    def todos(self, bot, update, args):
        '''Mandar un mensaje a todos los usuarios cuando el comando /todos es enviado.'''

        from telegram import ParseMode
        import time

        tiempo_actual = round(time.time())

        # Comprobamos si hay un tiempo final fijado y si el tiempo actual no lo sobrepasó:
        if self.tiempo_final != None:
            if tiempo_actual >= self.tiempo_final:
                self.tiempo_final = None

        # Si no hay un tiempo final fijado, podemos usar la función:
        if self.tiempo_final == None:
            from frases import usuarios
            mensaje_user = ' '.join(args)
            update.message.reply_text("<b>{0}</b>\n\n{1}".format(usuarios, mensaje_user),
                                      quote=False, parse_mode=ParseMode.HTML)
        
        # En caso de si haberlo, lo advertimos:
        else:
            from frases import mensajes_no_jodas

            tiempo_restante = round(self.tiempo_final-tiempo_actual)
            unidad = "segundos"

            if tiempo_restante >= 60 and tiempo_restante < 3600:
                tiempo_restante = round(tiempo_restante / 60)
                unidad = "minutos"

            update.message.reply_text("<i>Faltan como {0} {1} para poder usar /todos de nuevo.</i>".format(str(tiempo_restante), unidad),
                                      quote=False, parse_mode=ParseMode.HTML)
            update.message.reply_text("<i>{0}</i>".format(self.frase_al_azar(mensajes_no_jodas)),
                                      quote=False, parse_mode=ParseMode.HTML)


    def nojodan(self, bot, update, args):
        '''Cancela la función '/todos' por X tiempo y manda mensaje avisando dicha cancelación.'''
        
        from telegram import ParseMode
        from frases import mensajes_no_jodas, unidades
        import time

        tiempo_actual = round(time.time())

        # En casi de haber un tiempo establecido...
        if self.tiempo_final: 
            if tiempo_actual < self.tiempo_final:

                tiempo_restante = round(self.tiempo_final-tiempo_actual)
                unidad = "segundos"

                if tiempo_restante >= 60 and tiempo_restante < 3600:
                    tiempo_restante = round(tiempo_restante / 60)
                    unidad = "minutos"

                update.message.reply_text("<i>No se puede usar de nuevo hasta que no pase el tiempo anteriormente fijado (falta {0} {1}).</i>".format(str(tiempo_restante), unidad), 
                                          quote=False, parse_mode=ParseMode.HTML)
                update.message.reply_text("<i>{0}</i>".format(self.frase_al_azar(mensajes_no_jodas)), 
                                          quote=False, parse_mode=ParseMode.HTML)

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
                        update.message.reply_text("<i>No entendí el valor y/o la unidad que me pasaste, asi que ahora te jodes y pongo lo que se me canta.</i>",
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
                update.message.reply_text("<i>¿¡{0} {1}!? Dale bola, pasame un tiempo razonable.</i>".format(str(tiempo), unidad),
                                          quote=False, parse_mode=ParseMode.HTML)
                return

            # Si el tiempo se excede de un día, lo limitamos entonces a 1 hora:
            if tiempo_en_seg > 3600:
                update.message.reply_text("<i>No lo voy a poner en {0} {1} ni en pedo, olvidate.</i>".format(str(tiempo), unidad),
                                          quote=False, parse_mode=ParseMode.HTML)
                tiempo = 1
                unidad = "hora"
                tiempo_en_seg = tiempo * unidades[unidad]

            # Seteando tiempo final:
            self.tiempo_final = tiempo_actual + tiempo_en_seg
            update.message.reply_text("<i>La función /todos fue desactivada por {0} {1}.</i>".format(str(tiempo), unidad),
                                      quote=False, parse_mode=ParseMode.HTML)


    def error(self, bot, update, error):
        '''Loguea errores causados por Update's.'''

        self.logger.warning("Update '%s' caused error '%s'", update, error)


if __name__ == '__main__':
    
    # Tomando argumentos desde consola:
    import sys
    api_bot = sys.argv[1]
    api_weather = sys.argv[2]

    # Si se obtuvo los argumentos necesarios...
    if api_bot and api_weather:
        bot = Bot(api_bot, api_weather)

    # En caso contrario...
    else:
        print("\nError: no se pasaron todas las API's necesarias.")
        print("Abortando.\n")
