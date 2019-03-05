# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
import alsaaudio, wave, numpy
import os , time, datetime
import speech_recognition as sr
from os import path
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


WIT_AI_KEY = ""

# Pins definitions
btn_pin = 4
#led_pin = 12

# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(btn_pin, GPIO.IN)
GPIO.setup(27, GPIO.OUT) # el led
GPIO.output(27, False)

temperatura = ['temperatura', 'calor', 'calor']
humedad = ['humedad', 'húmedo','humedo','umedo']
wikipedia = ['wikipedia', 'Wikipedia', "wiki", "Wiki"]
terremoto = ['Terremoto', 'terremoto', "temblor", "Temblor", "sismo"]
encender = [ "Prender", "prender","encender", "Encender", "on"]
apagar = [ "Apagar", "apagar","off", "of"]
est_inter = [ "Estación", "estación", "estacion"]
noticias = [ "Noticias", "noticias", "novedades", "Novedades"]

class buscar_res:
	def __init__(self, texto , tema):
		self.texto = texto
		self.tema = tema

	# para encontrar la temperatura
	def decir_temperatura(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			if clave in self.tema:
				os.system("sudo pigpiod") # esto inicia el servicio de lectura de sensor 
				os.system("sudo python3 DHT22_tem.py")
				os.system("sudo killall pigpiod")


	# para encontrar la humedad
	def decir_humedad(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			if clave in self.tema:
				os.system("sudo pigpiod") # esto inicia el servicio de lectura de sensor 
				os.system("sudo python3 DHT22_hum.py")
				os.system("sudo killall pigpiod")

	# buscar en wikipedia			
	def buscar_wiki(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			#print "-----------------------------------"
			if clave in self.tema:
				buscar = self.texto[i+1:] # busca la palabras después de Wikipedia
				salida = ' '.join(map(str, buscar))
				print "Palabras claves: " + salida 
				buscar_wiki = "sudo python3 -W ignore wiki.py " + "'" + salida + "'"				
				os.system(buscar_wiki)

	# terremoto			
	def decir_terremoto(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			if clave in self.tema:			
				os.system("sudo python3 -W ignore terremoto.py")

	# encender luz			
	def encender_luz(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			if clave in self.tema:				
				#os.system("sudo python3 DHT22_hum.py")
				print "...Prendiendo la luz..."
				GPIO.output(27, True) #encineo la luz

	# apagar  luz			
	def apagar_luz(self):
		for i in range(len(self.texto)):
			clave = self.texto[i]
			if clave in self.tema:				
				#os.system("sudo python3 DHT22_hum.py")
				print "...Apagando la luz..."
				GPIO.output(27, False) #encineo la luz	
					# apagar  luz	

	#ISS						
	def estacion_espacial(self):
		#print " estamos en ISS"	
		for j in range(len(self.texto)):
			clave = self.texto[j]
			#print " clave :" + clave	
			if clave in self.tema:	
				buscar = self.texto[j:]
				salida = ' '.join(map(str, buscar))
				if 	salida in ['Estación espacial',
							'estación espacial',
							'Estación espacial internacional',
							'estación espacial internacional']:
							#print "final : " + salida		
							os.system("sudo python3 -W ignore tracknew.py")	
	#noticias de salud						
	def noticias(self):
		#print " estamos en ISS"	
		for j in range(len(self.texto)):
			clave = self.texto[j]
			#print " clave :" + clave	
			if clave in self.tema:	
				buscar = self.texto[j+2:]
				salida = ' '.join(map(str, buscar))
				if 	salida in ['medicina','Medicina','Salud','salud']:
					#print "final : " + salida		
					os.system("sudo python3 -W ignore salud_titulos.py")
				if 	salida in ['tecnología','Tecnología','tecnologia','Tecnologia']:
					#print "final : " + salida		
					os.system("sudo python3 -W ignore tecnologia_titulos.py")	
				if 	salida in ['Ciencia','ciencia','Ciencias','ciencias']:
					#print "final : " + salida		
					os.system("sudo python3 -W ignore ciencia_titulos.py")
				if 	salida in ['Política','politia','política','Politica']:
					#print "final : " + salida		
					os.system("sudo python3 -W ignore politica_titulos.py")		


activo = 0
prev_input = 0
try:
	while True:
		input = GPIO.input(4)
		if ((not prev_input) and input) and activo == 0:	
			inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
			inp.setchannels(1)
			inp.setrate(44100)
			#inp.setrate(8000)
			inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
			inp.setperiodsize(1024)
			w = wave.open('temp.wav', 'w')
			w.setnchannels(1)
			w.setsampwidth(2)
			w.setframerate(44100)
			#w.setframerate(8000)
			os.system("aplay --device=plughw:1,0 beep.wav -q")
			activo = 1
			print "...Grabando ..."
		if (GPIO.input(4) == True) and activo == 1:
			l, data = inp.read()
			w.writeframes(data)
		if (prev_input and not input):
			activo = 0
			time.sleep(1) #este delay impide error al enviar datos
			os.system("aplay --device=plughw:1,0 beep.wav -q") # -q permite ocultar la imformación de archivo
			print "...Enviando datos a Wit..."
			inp.close()
			w.close()
			AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "temp.wav")
			r = sr.Recognizer()
			with sr.AudioFile(AUDIO_FILE) as source:
	  			audio = r.record(source) # read the entire audio file
	  		responder = r.recognize_wit(audio, key=WIT_AI_KEY)
			print "..."+ responder + "..."			
			f = open("temp.txt","w")
			f.write(" "+ responder)
			f.close()
			#buscar_respuesta(responder)
			
			temp = buscar_res( responder.split(' '), temperatura)
			hum = buscar_res( responder.split(' '), humedad)
			wiki = buscar_res( responder.split(' '), wikipedia)
			temblor = buscar_res( responder.split(' '), terremoto)
			luz_on = buscar_res( responder.split(' '), encender)
			luz_off = buscar_res( responder.split(' '), apagar)
			iss = buscar_res( responder.split(' '), est_inter)
			news = buscar_res( responder.split(' '), noticias)


			temp.decir_temperatura()
			hum.decir_humedad()
			wiki.buscar_wiki()
			temblor.decir_terremoto()
			luz_on.encender_luz()
			luz_off.apagar_luz()
			iss.estacion_espacial()
			news.noticias()

			#os.system("sudo python3 habla.py")
			os.system("aplay --device=plughw:1,0 beep.wav -q") 

		prev_input = input	

# When you press ctrl+c, this will be called


except KeyboardInterrupt:
	GPIO.cleanup()
