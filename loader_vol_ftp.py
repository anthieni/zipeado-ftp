#enconding: utf-8
"""
comprime los datos de entrada y los sube a un ftp, luego guarda los datos
"""


#Cargo librerias
import os
import datetime
import time
import sys, traceback
import shutil
import zipfile


import logging
from ftplib import FTP
from ftplib import error_perm



import global_variables as gv


###########################################################################################
###########################################################################################



#Definicion de Variables
fecha_hora= str(time.strftime("%Y-%m-%d%H:%M:%S"))

#Rutas por defecto

rutaOrigen = '/opt/datos/input/'
rutaDestino = '/opt/datos/output/'
rutaZipDestino = '/opt/datos/zip_output/'
rutaTemp = '/opt/datos/temp/'
rutaLog = '/opt/datos/log/'

#Inicio de los logger
logging.basicConfig(format='%(asctime)s %(message)s')
logging.basicConfig(filename=rutaLog+'registro.log',level=logging.DEBUG)


#Creamos el zip con todos los archivos .vol disponibles

try:


    #Creamos el zip con todos los archivos extraidos
    os.chdir(rutaTemp)  #cambiar al directorio donde quiero crear la carpeta zip

    zfilename = fecha_hora + '_vol.zip'

    zf = zipfile.ZipFile(zfilename, "w")

    for dirname, subdirs, files in os.walk(rutaOrigen):
        #zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename),filename)
    zf.close()


    logging.info("se comprimio correctamente el archivo: "+zfilename)
except:

    logging.error("Error al comprimir el archivo: "+zfilename)


#conecto con el FTP

try:
    ftpOrigen = FTP(gv.hostFTP,gv.userFTP, gv.passFTP)
    #ftpOrigen.login(gv.userFTP, gv.passFTP)
    ftpOrigen.cwd(gv.dirFTP)
    logging.info("Conexion exitosa al FTP")

    #Cargo el archivo al repositorio de procesado
    #upload(ftpOrigen, rutaTemp, zfilename)

    file = open(rutaTemp+zfilename,'rb')
    ftpOrigen.storbinary('STOR '+zfilename,file)
    file.close()

    logging.info("Se subio correctamente el archivo: "+zfilename)

    #Cierro la conexion del FTP
    ftpOrigen.quit()
    logging.info("cierro el ftp")

except Exception:
    logging.error("Error en la conexion de FTP")
    logging.error(traceback.print_exc(file=sys.stdout))

try:
    #Termino de acomodar los archivos

    #muevo el archivo a producto terminado
    shutil.move(rutaTemp+zfilename, rutaZipDestino + zfilename)

    #muevo los archivos .vol

    #creo el directorio
    os.makedirs(rutaDestino+fecha_hora, exist_ok=True)

    #muevo los archivos de un directorio al otro
    files = os.listdir(rutaOrigen)
    for f in files:
        shutil.move(rutaOrigen+f, rutaDestino+fecha_hora)

    logging.info("muevo los archivos a sus correspondientes destinos")

except:
    logging.error("no se pudo mover los archivos a destino")

logging.info("fin del proceso")
