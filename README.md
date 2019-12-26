# Switchbot_Py_Meter
Python script to read temperature and humidity from Switchbot Meter and send via MQTT (for Home Assistant etc)

You will need:
1. Python3
2. BluePy library (https://github.com/IanHarvey/bluepy)
3. Paho MQTT Library (https://github.com/eclipse/paho.mqtt.python)

Edit meters.py to add your configuration information:
1. Switchbot Meter Mac Addresses & "rooms".
2. MQTT Server address & login
3. Once running OK, change debug_level to 0. 

MQTT Topic example: room1/meter
Payload example: {"time":"2019-12-26 08:20:06","temperature":20.1,"humidity":54}

Run command is: 
Sudo Python3 meters.py


