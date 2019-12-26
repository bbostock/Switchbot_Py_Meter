#!/usr/bin/python3
from __future__ import print_function
import argparse
import binascii
import os
import sys
import time
import datetime
from bluepy import btle
import paho.mqtt.client as mqtt

METER_ROOMS = ['Bathroom','SunRoom','Entrance','Kitchen','LivingRoom','Hall','SpareBedroom']
METER_MACS = ['f1:cd:a6:4c:7a:8d','e7:c8:1e:43:66:7e','d2:6b:6d:2d:9e:e9','c1:1c:4f:3b:c9:10','c9:f4:a3:7e:63:91','f5:db:3b:53:66:ce','f7:ef:3e:d3:8b:8b']
MQTT_USERNAME = 'bbostock'
MQTT_PASSWORD = 'hcwl4HH'
MQTT_HOST = '192.168.1.125'
MQTT_PORT = 1883
MQTT_TIMEOUT = 30 #60
MQTT_TOPIC_STACK = {""}
MQTT_PAYLOAD_STACK = {""}
debug_level = 0

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'


class ScanProcessor():

    def __init__(self):
        self.mqtt_client = None
        self.connected = False
        self._start_client()


    def handleDiscovery(self, dev, isNewDev, isNewData):
        try:
            if isNewDev and dev.addr in METER_MACS:
                i = 0
                room = METER_ROOMS[METER_MACS.index(dev.addr)]
                if debug_level == 1:
                    print ('\nRoom: %s Device: %s (%s), %d dBm %s. ' %(ANSI_WHITE + room + ANSI_OFF,ANSI_WHITE + dev.addr + ANSI_OFF,dev.addrType,dev.rssi,('' if dev.connectable else '(not connectable)')), end='')
                for (sdid, desc, value) in dev.getScanData():
                    #000d540064009435
                    i=i+1
                    #print( str(i) + ': ' + str(sdid) + ', '+ desc + ', ' + value)
                    #Model T (WOSensorTH) example Service Data: 000d54006400962c
                    if desc == '16b Service Data':
                        if value.startswith('000d'):
                            model = binascii.a2b_hex(value[4:6])
                            mode = binascii.a2b_hex(value[6:8])
                            byte3 = int(value[10:12],16)
                            byte4 = int(value[12:14],16)
                            byte5 = int(value[14:16],16)
                            tempc = float(byte4-128)+float(byte3 / 10.0)
                            humidity = byte5
                            if debug_level == 1:
                                print('\nPublishing...'+room)
                            self._publish(room, tempc, humidity)
     
                        else:
                            if debug_level == 1:
                                print(value.len())
    
                    #else:
                        #print('Not 16b Service Data')
    
                if not dev.scanData:
                    print ('(no data)')
                    print

        except:
            print("handleDiscovery: Oops!",sys.exc_info()[0],"occurred.")


    def _start_client(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        def _on_connect(client, _, flags, return_code):
            self.connected = True
            #print("on_connect: MQTT connection returned result: %s" % mqtt.connack_string(return_code))

        def on_disconnect(client, userdata, return_code):
            if rc != 0:
                print("Unexpected disconnection: "+ return_code)
            else:
                print("Disconnected.")

        def _on_publish(client, userdata, mid):
            info = 'on_publish: {}, {}, {}'.format(client,userdata,str(mid))
            #print(info)

        def _on_log(mqttc, obj, level, string):
            if debug_level == 1:
                print('on_log: ' + string)

        self.mqtt_client.on_connect = _on_connect
        self.mqtt_client.on_publish = _on_publish
        self.mqtt_client.on_log = _on_log

        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT)
        self.mqtt_client.loop_start()

    def _publish(self, room, tempc, humidity):
        try:
            now = datetime.datetime.now()
            topic = '{}/{}'.format(room.lower(), 'meter')
            timeNow = now.strftime("%Y-%m-%d %H:%M:%S")
            msgdata = '{"time":\"' + timeNow + '\","temperature":' + str(tempc) + ',"humidity":' + str(humidity) + '}'
            MQTT_TOPIC_STACK.add(topic)
            MQTT_PAYLOAD_STACK.add(msgdata)
            if self.connected:
                while len(MQTT_TOPIC_STACK) > 0:
                    t = MQTT_TOPIC_STACK.pop()
                    p = MQTT_PAYLOAD_STACK.pop()
                    if len(t) > 0:
                        if debug_level == 1:
                            print('STACK {} {} {} {} '.format(str(len(MQTT_TOPIC_STACK)),timeNow,t,p))
                        self.mqtt_client.publish(t, p, qos=0, retain=True)
                        print('Sent data to topic %s: %s ' % (topic, msgdata))
        except:
            print("_publish: Oops!",sys.exc_info()[0],"occurred.")

#    def _publish(self, room, tempc, humidity):
#        if not self.connected:
#            raise Exception('not connected to MQTT server')

#        try:
#            now = datetime.datetime.now()
#            topic = '{}/{}/{}'.format(room.lower(), 'meter', 'temperature')
#            msgdata = '{"time":' + now.strftime("%Y-%m-%d %H:%M:%S") + '"temperature":' + str(tempc) + ',"humidity":' + str(humidity) + '}'
#            #msgdata = '{}/{}'.format(str(tempc),str(humidity))
#            self.mqtt_client.publish(topic, msgdata, qos=0, retain=True)
#            print('Sent data to topic %s: %s ' % (topic, msgdata))
#        except:
#            print("Oops!",sys.exc_info()[0],"occurred.")


def main():

    scanner = btle.Scanner().withDelegate(ScanProcessor())

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(30)

if __name__ == "__main__":
        main()
