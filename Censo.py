#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
# BOT DE ESCANEO                                                               #
#------------------------------------------------------------------------------#
# Si se le reenvía un mensaje de un canal reenvía todos los mensajes           #
# para que puedan ser analizados y catalogados                                 #
################################################################################
import telebot
from telebot import types
import json
import logging
import time

#-------------------------------------------------------------------------------
# VARIABLES AUXILIARES
#-------------------------------------------------------------------------------
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'   # Cambiar por el token del bot
CHAT_censo = 9999999999             # ID del canal a censar
CHAT_biblioteca = 9999999999            # ID del canal donde se recopila la información
f_mens = "./ult_mensaje_tratado"
f_docs = "./censo_documentos"
f_fileids = "./fileids"
last_msg = 0

logging.basicConfig(filename='./BOT_Envio.log',level=logging.DEBUG)
logging.info("-------------------------------------------------------------------")
logging.info("COMIENZO DE PROCESO")
logging.info("-------------------------------------------------------------------")
#-------------------------------------------------------------------------------
# FORMATO DEL REGISTRO A GRABAR EN EL CENSO DE DOCUMENTOS
#   cid         codigo identificador del chat donde reside el documento
#   mid         codigo identificador del mensaje
#   mtp         tipo de documento
#   nom         nombre del documento
#   siz         tamaño del documento
#   lnk1        enlace del chat original
#   fileid1     codigo de identificacion del fichero en el chat
#   lnk2        enlace de Librería del Caos
#   fileid2     codigo de identificacion del fichero en el chat
#   ufileid     código de identificador UNICO del fichero en Telegram
reg_f_docs = "{cid};{mid};{mtp};{nom};{siz};https://t.me/{cnm1}/{mid1};{fileid1};https://t.me/{cnm2}/{mid2};{fileid2};{ufileid}"

#-------------------------------------------------------------------------------
# Valida los mensajes recibidos y reenvía y censa los que sean documentos
#-------------------------------------------------------------------------------
def listener(mensajes):
    with open(f_docs, "a") as file2:
        for m in mensajes:
            chat_name = m.chat.username

            if (m.content_type == "document"):
                print("    --> Es documento tipo " + str(m.document.mime_type))
                logging.info("    --> Es documento tipo " + str(m.document.mime_type))

            if (m.content_type == "document") and (("application" in str(m.document.mime_type)) or (m.document.mime_type == None)):
                print("    --> Entra al proceso de reenvío")
                print("-------------------------------------------------------------------")
                print(json.dumps(m.json, indent=4))
                print("-------------------------------------------------------------------")

                logging.info("    --> Entra al proceso de reenvío")
                logging.info("-------------------------------------------------------------------")
                logging.info(json.dumps(m.json, indent=4))
                logging.info("-------------------------------------------------------------------")

                cid = m.chat.id
                mid = m.message_id
                mtp = str(m.document.mime_type)
                siz = m.document.file_size
                cnm1 = m.chat.username
                mid1 = mid
                fileid1 = m.document.file_id
                dic1 = m.json
                dic2 = dic1["document"]
                ufileid = dic2["file_unique_id"]
                nom = dic2["file_name"].encode('utf-8')

                fileids = recuperar_fileids()

                if ufileid + "\n" not in fileids:
                    # Reenvía el mensaje a la Liberia del Caos
                    fm = bot.forward_message(CHAT_biblioteca, cid, mid, disable_notification=True)

                    cnm2 = fm.chat.username
                    mid2 = fm.message_id
                    fileid2 = fm.document.file_id

                    r = reg_f_docs.format(cid=cid, mid=mid, mtp=mtp,nom=nom,siz=siz,
                            cnm1=cnm1,mid1=mid1,fileid1=fileid1,
                            cnm2=cnm2,mid2=mid2,fileid2=fileid2,
                            ufileid=ufileid)

                    file2.write(r + "\n")

                    fileids.append(ufileid + "\n")
                    with open(f_fileids, "a") as file3:
                        file3.write(ufileid + "\n")

def recuperar_fileids():
    with open(f_fileids, "r") as file3:
        return file3.readlines()

#-------------------------------------------------------------------------------
# PROCESO PRINCIPAL
#-------------------------------------------------------------------------------
bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)

# COMANDO '/START' -------------------------------------------------------------
@bot.message_handler(commands=['start'])
def func_start(m):
    cid = m.chat.id
    chat_name = m.chat.username
    uid = m.from_user.id
    mid = m.message_id

    # Si no está censado el canal crea los ficheros para censar

    # print("-------------------------------------------------------------------")
    # print(json.dumps(m.json, indent=4))
    # print("-------------------------------------------------------------------")

    bot.send_message(cid,"¡Hola!\nSoy un bot de apoyo para censar los libros del grupo y copiarlos a la nueva Biblioteca .\n\n- Para *comenzar el proceso* pulsa /censar\n- Para *exportar* el fichero resultante (transportable a Excel) pulsa /exportar",  parse_mode="Markdown")

@bot.message_handler(commands=['censar'])
def func_censar(m):
    if validar_usuario(m) == True:
        cid = -99999999999999            # Cambiar por el ID del grupo a censar
        chat_name = "xxxxxxxxxx"         # Cambiar por el nombre del grupo a censar
        uid = m.from_user.id
        mid = m.message_id

        # Borra el mensaje tecleado
        # bot.delete_message(cid,mid)

        # Recupera el último mensaje tratado del fichero
        with open(f_mens, "r") as file1:
            last_msg = int(file1.readline())

            # print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
            # print(last_msg)
            # print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")

        # if last_msg == 0:
        #     last_msg = mid

        # print("-------------------------------------------------------------------")
        # print(json.dumps(m.json, indent=4))
        # print("-------------------------------------------------------------------")

        with open(f_docs, "a") as file2:
            for i in range (last_msg -1, 1, -1):
                # Escribe el mensaje a tratar en el fichero ./listado_mensajes
                with open(f_mens, "w") as file1:
                    file1.write(str(i))

                print("-------------------------------------------------------------------")
                print("Procesando mensaje: " + str(i))

                logging.info("-------------------------------------------------------------------")
                logging.info("Procesando mensaje: " + str(i))

                # Reenvía el mensaje para que sea tratado en el otro chat.
                fm = bot.forward_message(CHAT_biblioteca, cid, i, disable_notification=True)

                # print("-------------------------------------------------------------------")
                # print(json.dumps(fm.json, indent=4))
                # print("-------------------------------------------------------------------")

                if (fm.content_type == "document"):
                    print("    --> Es documento tipo " + str(fm.document.mime_type))
                    logging.info("    --> Es documento tipo " + str(fm.document.mime_type))

                if (fm.content_type == "document") and (("application" in str(fm.document.mime_type)) or (fm.document.mime_type == None)):
                    print("    --> Entra al proceso de reenvío")
                    print("-------------------------------------------------------------------")
                    print(json.dumps(fm.json, indent=4))
                    print("-------------------------------------------------------------------")

                    logging.info("    --> Entra al proceso de reenvío")
                    logging.info("-------------------------------------------------------------------")
                    logging.info(json.dumps(fm.json, indent=4))
                    logging.info("-------------------------------------------------------------------")

                    fileids = recuperar_fileids()

                    mtp = str(fm.document.mime_type)
                    siz = fm.document.file_size
                    cnm1 = "magiacaos"
                    mid1 = i
                    fileid1 = fm.document.file_id
                    dic1 = fm.json
                    dic2 = dic1["document"]
                    ufileid = dic2["file_unique_id"]
                    nom = dic2["file_name"].encode('utf-8')
                    cnm2 = fm.chat.username
                    mid2 = fm.message_id
                    fileid2 = fm.document.file_id

                    r = reg_f_docs.format(cid=cid, mid=mid1, mtp=mtp,nom=nom,siz=siz,
                            cnm1=cnm1,mid1=mid1,fileid1=fileid1,
                            cnm2=cnm2,mid2=mid2,fileid2=fileid2,
                            ufileid=ufileid)

                    if ufileid + "\n" not in fileids:
                        # Censa el documento
                        file2.write(r + "\n")

                        fileids.append(ufileid + "\n")
                        with open(f_fileids, "a") as file3:
                            file3.write(ufileid + "\n")
                    else:
                        # Borra el mensaje reenviado por estar repetido
                        bot.delete_message(CHAT_biblioteca, fm.message_id)
                else:
                    # Borra el mensaje reenviado si no es documento
                    bot.delete_message(CHAT_biblioteca, fm.message_id)

                print("-------------------------------------------------------------------")
                logging.info("-------------------------------------------------------------------")

# bot.polling()
# bot.polling(none_stop=True,interval=300)
bot.polling(none_stop=True)
