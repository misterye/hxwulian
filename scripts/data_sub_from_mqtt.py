import os

os.system("mosquitto_sub -t 'devices/raspi/#' -d")
