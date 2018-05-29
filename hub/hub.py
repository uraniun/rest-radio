import sys, struct, json, re
from auto_detector import auto_detect_microbit
from radio_packet import RadioPacket
from request_handler import RequestHandler
from endpoint_poller import EndpointPoller
from cloud_variable_ep import CloudVariableEp
from serial_handler import SerialHandler
from pearson import pearson_hash
from time import sleep

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

auto_detect = True
# if auto-detect is False, this path will be used.
selected = "/dev/cu.usbmodem1462"

if auto_detect:
    selected = auto_detect_microbit()

    if selected is None:
        raise Exception("No Bridge Detected")

translations = open("./translations.json")
translations = json.load(translations)

cloud_variable_ep = CloudVariableEp(hub_variables)

#this class can be used to poll an endpoint, I didn't find a real use for it.
# ep_poller = EndpointPoller(translations, hub_variables)

serial_handler = SerialHandler(selected)

# while true swap between polling EPs and receiving / sending.
while(True):

    # if the bridged micro:bit has sent us data, process
    if serial_handler.buffered() > 0:
        rPacket = RadioPacket(serial_handler.read_packet())
        requestHandler = RequestHandler(rPacket,translations, hub_variables, cloud_variable_ep)
        bytes = requestHandler.handleRequest()
        serial_handler.write_packet(bytes)
    else:
    # otherwise check if our asynchronous socket io ep has packets to transmit.
        bytes = cloud_variable_ep.drain()

        if len(bytes) > 0:
            serial_handler.write_packet(bytes)

    # prevent burning the processor :)
    sleep(0.01)

