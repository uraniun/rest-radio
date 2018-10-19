#!/usr/bin/python

import os
import sys, struct, json, re, pickle
from auto_detector import auto_detect_microbit
from radio_packet import RadioPacket
from request_handler import RequestHandler
from endpoint_poller import EndpointPoller
from cloud_variable_ep import CloudVariableEp
from serial_handler import SerialHandler
from pearson import pearson_hash
from time import sleep
from pathlib import Path

# this struct is passed to class instances for general use.
hub_variables = {
    # Variables attached to the query_string object will be inserted into query strings
    "query_string":{
        "school_id":"123456789"
    },
    "cloud_variable_socket":{
        "address":"localhost",
        "port":8001,
    }
}



auto_detect = False
# if auto-detect is False, this path will be used.
selected = "/dev/ttyACM0"

if auto_detect:
    selected = auto_detect_microbit()

    if selected is None:
        raise Exception("No Bridge Detected")



#cloud_variable_ep = CloudVariableEp(hub_variables)

#this class can be used to poll an endpoint, I didn't find a real use for it.
# ep_poller = EndpointPoller(translations, hub_variables)

try:
    port1 = "/dev/ttyACM1"
    port2 = "/dev/ttyACM2"
    ioPort = Path(selected)
    ioPort1 = Path(port1)
    ioPort2 = Path(port2)
    if ioPort.exists():
        serial_handler = SerialHandler(selected)
    elif ioPort1.exists():
        serial_handler = SerialHandler(port1)
    elif ioPort2.exists():
        serial_handler = SerialHandler(port2)
        
    # load translations JSON file
    translationsFile = open("./translations.json")
    translations = json.load(translationsFile)
    
    # while true swap between polling EPs and receiving / sending.
    
    while(True):
        
        # if the bridged micro:bit has sent us data, process
        if serial_handler.buffered() > 0:
            rPacket = RadioPacket(serial_handler.read_packet())
            requestHandler = RequestHandler(rPacket,translations, hub_variables, None)
            bytes = requestHandler.handleRequest()
            serial_handler.write_packet(bytes)
 #   else:
    # otherwise check if our asynchronous socket io ep has packets to transmit.
  #      bytes = cloud_variable_ep.drain()

   #     if len(bytes) > 0:
    #        serial_handler.write_packet(bytes)

    # prevent burning the processor :)
        sleep(0.01)

except KeyboardInterrupt:
    print "Voluntary Quit"
except Exception as e:
    print " Quit with exception " + str(e)
    try:
        sleep(5)
        os.execv('/home/pi/Documents/Projects/rest-radio/hub/hub.py',[''])
    except KeyboardInterrupt:
        print "Voluntary final Quit"
    except Exception as e:
        print " Quit with final exception " + str(e)
