import sys, struct, json, re
from radio_packet import RadioPacket
from request_handler import RequestHandler
from endpoint_poller import EndpointPoller
from serial_handler import SerialHandler

from time import sleep

import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print p

hub_variables = {
    "school_id":"123456789"
}

translations = open("./translations.json")
translations = json.load(translations)

ep_poller = EndpointPoller(translations, hub_variables)
while True:

    poll_results = ep_poller.poll()
    print poll_results
    sleep(1)

serial_handler = SerialHandler("/dev/cu.usbmodem1412")

# while true swap between polling EPs and receiving / sending.
while(True):
    if serial_handler.buffered() > 0:
        rPacket = RadioPacket(serial_handler.read_packet())
        requestHandler = RequestHandler(rPacket,translations)
        bytes = requestHandler.handleRequest()
        serial_handler.write_packet(bytes)
    else:
        poll_results = ep_poller.poll()

        #not correct, but desired semantics.
        for c in poll_results:
            serial_handler.write_packet(c)


