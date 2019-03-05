#!/usr/bin/env python

# 2014-07-11 DHT22.py

import time
import atexit
import boto3
import os
import pigpio

polly_client = boto3.Session(
    aws_access_key_id= '',                     
    aws_secret_access_key='',
    region_name='us-west-2').client('polly')

def speak(text):
        text = text.strip()
        if len(text) == 0:
                return
        voice = pyvona.create_voice(awsAccessKey, awsSecretKey)
        voice.voice_name = "Penelope"
        voice.speak(text)


class sensor:

      diff = pigpio.tickDiff(self.high_tick, tick)

      if level == 0:

         # Edge length determines if bit is 1 or 0.

         if diff >= 50:
            val = 1
            if diff >= 200:   # Bad bit?
               self.CS = 256  # Force bad checksum.
         else:
            val = 0

         if self.bit >= 40:  # Message complete.
            self.bit = 40

         elif self.bit >= 32:  # In checksum byte.
            self.CS  = (self.CS << 1)  + val

            if self.bit == 39:

               # 40th bit received.

               self.pi.set_watchdog(self.gpio, 0)

               self.no_response = 0

               total = self.hH + self.hL + self.tH + self.tL

               if (total & 255) == self.CS:  # Is checksum ok?

                  self.rhum = ((self.hH << 8) + self.hL) * 0.1

                  if self.tH & 128:  # Negative temperature.
                     mult = -0.1
                     self.tH = self.tH & 127
                  else:
                     mult = 0.1

                  self.temp = ((self.tH << 8) + self.tL) * mult

                  self.tov = time.time()

                  if self.LED is not None:
                     self.pi.write(self.LED, 0)

               else:

                  self.bad_CS += 1

         elif self.bit >= 24:  # in temp low byte
            self.tL = (self.tL << 1) + val

         elif self.bit >= 16:  # in temp high byte
            self.tH = (self.tH << 1) + val

         elif self.bit >= 8:  # in humidity low byte
            self.hL = (self.hL << 1) + val

         elif self.bit >= 0:  # in humidity high byte
            self.hH = (self.hH << 1) + val

         else:               # header bits
            pass

         self.bit += 1

      elif level == 1:
         self.high_tick = tick
         if diff > 250000:
            self.bit = -2
            self.hH = 0
            self.hL = 0
            self.tH = 0
            self.tL = 0
            self.CS = 0

      else:  # level == pigpio.TIMEOUT:
         self.pi.set_watchdog(self.gpio, 0)
         if self.bit < 8:       # Too few data bits received.
            self.bad_MM += 1    # Bump missing message count.
            self.no_response += 1
            if self.no_response > self.MAX_NO_RESPONSE:
               self.no_response = 0
               self.bad_SR += 1  # Bump sensor reset count.
               if self.power is not None:
                  self.powered = False
                  self.pi.write(self.power, 0)
                  time.sleep(2)
                  self.pi.write(self.power, 1)
                  time.sleep(2)
                  self.powered = True
         elif self.bit < 39:    # Short message receieved.
            self.bad_SM += 1    # Bump short message count.
            self.no_response = 0

         else:                  # Full message received.
            self.no_response = 0

   def temperature(self):
      """Return current temperature."""
      return self.temp

   def humidity(self):
      """Return current relative humidity."""
      return self.rhum

   def staleness(self):
      """Return time since measurement made."""
      if self.tov is not None:
         return time.time() - self.tov
      else:
         return -999

   def bad_checksum(self):
      """Return count of messages received with bad checksums."""
      return self.bad_CS

   def short_message(self):
      """Return count of short messages."""
      return self.bad_SM

   def missing_message(self):
      """Return count of missing messages."""
      return self.bad_MM

   def sensor_resets(self):
      """Return count of power cycles because of sensor hangs."""
      return self.bad_SR

   def trigger(self):
      """Trigger a new relative humidity and temperature reading."""
      if self.powered:
         if self.LED is not None:
            self.pi.write(self.LED, 1)

         self.pi.write(self.gpio, pigpio.LOW)
         time.sleep(0.017)  # 17 ms
         self.pi.set_mode(self.gpio, pigpio.INPUT)
         self.pi.set_watchdog(self.gpio, 200)

   def cancel(self):
      """Cancel the DHT22 sensor."""

      self.pi.set_watchdog(self.gpio, 0)

      if self.cb is not None:
         self.cb.cancel()
         self.cb = None

if __name__ == "__main__":

   import time

   import pigpio

   import DHT22

   # Intervals of about 2 seconds or less will eventually hang the DHT22.
   INTERVAL = 3

   pi = pigpio.pi()

   s = DHT22.sensor(pi, 22, LED=16, power=8)

   r = 0

   s.trigger()

   time.sleep(1)

   print(round(s.humidity(),1))

   response = polly_client.synthesize_speech(
      VoiceId='Mia',
      OutputFormat='mp3', 
      Text = 'La humedad actual es: ' + str(round(s.humidity(),1)) + ' porciento.')
   file = open('humedad.mp3', 'wb')
   file.write(response['AudioStream'].read())
   file.close()
   os.system("mpg123 -q humedad.mp3")

