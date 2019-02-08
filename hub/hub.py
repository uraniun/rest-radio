#!/usr/bin/python
import os, sys, struct, json, re, pickle, requests, datetime
from auto_detector import auto_detect_microbit
from radio_packet import RadioPacket
from request_handler import RequestHandler
from endpoint_poller import EndpointPoller
from cloud_variable_ep import CloudVariableEp
from url_poller import URLPoller
from serial_handler import SerialHandler
from pearson import pearson_hash
from time import sleep
from multiprocessing import Process, Manager

# this struct is passed to class instances for general use.
hub_variables = {
    "authenticated": False,
    # Variables attached to the query_string object will be inserted into query strings
    "query_string":{
        # by default our auth variables are empty, it will be populated by the auth micro:bit
        "school-id":"",
        "pi-id":""
    },
    "cloud_variable_socket":{
        "address":"localhost",
        "port":8001,
    },
    "translations_json":{
        "url" : "https://raw.githubusercontent.com/lancaster-university/rest-radio/master/hub/translations.json",
        "poll_time" : 60
    }
}
# this function is run when a packet is received by a separate process.
def handleRequest(requestHandler, serial_handler):
    bytes = requestHandler.handleRequest()

    if bytes is not None and len(bytes):
        serial_handler.lock()
        serial_handler.write_packet(bytes)
        serial_handler.unlock()

# we can share variables using a manager
shared_manager = Manager()
# make a shared variable, based on our preset hub_variables
# NOTE: when updating an inside dict, use the top level dictionary.
shared_dict = shared_manager.dict(hub_variables)

auto_detect = True
# if auto-detect is False, this path will be used.
selected = "/dev/cu.usbmodem1462"

if auto_detect:
    selected = auto_detect_microbit()

    if selected is None:
        raise Exception("No Bridge Detected")

serial_handler = SerialHandler(selected)

# load translations JSON file
translationsFile = open("./translations.json")
translations = json.load(translationsFile)
github_poller = URLPoller(hub_variables["translations_json"]["url"], hub_variables["translations_json"]["poll_time"])

packet_count = 0

try:
    while(True):

        # if the bridged micro:bit has sent us data, process
        if serial_handler.buffered() > 0:
            rPacket = RadioPacket(serial_handler.read_packet())

            packet_count += 1
            now = datetime.datetime.now()
            print "Request Time: %d:%d:%d; Packets Seen: %d" % (now.hour, now.minute, now.second, packet_count)

            requestHandler = RequestHandler(rPacket,translations, shared_dict, None)

            # spawn a new thread to handle the request
            p = Process(target=handleRequest, args=(requestHandler, serial_handler,))
            p.start()

        # every few minutes we check github for new translations.
        if github_poller.poll():

            temp_translations = github_poller.get_cached()
            if temp_translations["version"] <= translations["version"]:
                continue

            translations = temp_translations
            print "Updating translations from Github"

            with open("./translations-remote.json", 'w') as f:
                f.write(json.dumps(github_poller.get_cached(), indent=4, sort_keys=True))

        # prevent burning the processor :)
        sleep(0.01)
except Exception as e:
    print str(e)
    r = RadioPacket(None, app_id = 0, namespace_id = 0, uid = 0, request_type = RadioPacket.REQUEST_TYPE_HELLO)
    r.append(-1)
    serial_handler.write_packet(r.marshall(False))
