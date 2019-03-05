# -*- coding: utf-8 -*-

import os
import urllib3
import requests
import json
import datetime
import time
from googletrans import Translator
import sys
import boto3
import os

translator = Translator()

polly_client = boto3.Session(
    aws_access_key_id= '',                     
    aws_secret_access_key='',
    region_name='us-west-2').client('polly')



DEBUG    = 1       # Debug 0 off, 1 on
LOG      = 1       # Log Earthquake data for past 15 min
MINMAG   = 2.0     # Minimum magnitude to alert on


utcnow = datetime.datetime.utcnow()
utcnow_15 = utcnow - datetime.timedelta(minutes = 1)
utcnow_30 = utcnow - datetime.timedelta(minutes = 240)
starttime = utcnow_30.strftime('%Y-%m-%dT%H:%M:%S')
endtime = utcnow_15.strftime('%Y-%m-%dT%H:%M:%S')


try:

    quake_data = requests.get('http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson').json()

    
    data = quake_data 

    print(" _________________")

except:
    print("nada")


for feature in data['features']:
    if LOG:


        duracion = feature['properties']['time'] - feature['properties']['updated']
        duracionSegundos = datetime.datetime.utcfromtimestamp(int(duracion)).strftime('%H:%M:%S')

        tm  = feature['properties']['time']
        tm = tm/1000 - 18000            
        HoraDeLima = datetime.datetime.utcfromtimestamp(int(tm)).strftime('%H:%M:%S')

        mag = str(feature['properties']['mag'])
        lugar = feature['properties']['place']
        longitud = feature['geometry']['coordinates'][0]
        latitud = feature['geometry']['coordinates'][1]

        lugar_separado = lugar.split() 

        if feature['properties']['mag'] >= 4.8:
            print('Magnitud: ' + str(feature['properties']['mag']))

            el_lugar = str(lugar)
            ciudad = el_lugar.split(",")
            es_ciudad = translator.translate(ciudad[1], dest='es')

            print('Ubicado en: '  + str(es_ciudad.text))
            print('log: '  + str(longitud))
            print('lat: '  + str(latitud))

            f = open("mitexto.txt","w")
            f.write( mag +  ' : '  + 
                ciudad[1] + ' : '  + 
                str(longitud) + ' : ' +
                str(latitud) )
            f.close()
            time.sleep(1)
                        
            print('A las ' + str(HoraDeLima) + ', hora de Lima.')

            respuesta = "Se ha reportado un terremoto en:" + str(es_ciudad.text) + " de magnitud " + mag +" grados a las " + datetime.datetime.utcfromtimestamp(int(tm)).strftime('%H') + "horas" + datetime.datetime.utcfromtimestamp(int(tm)).strftime('%M') + " minutos."

            response = polly_client.synthesize_speech(
                VoiceId='Mia',
                OutputFormat='mp3', 
                Text = respuesta)

            file = open('terremoto.mp3', 'wb')
            file.write(response['AudioStream'].read())
            file.close()
            os.system("mpg123 -q terremoto.mp3")
            time.sleep(1)
            print("--------------")

    