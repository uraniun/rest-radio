#!/usr/bin/python
import os, sys, struct, json, re, pickle, requests
from auto_detector import auto_detect_microbit
from radio_packet import RadioPacket
from request_handler import RequestHandler
from endpoint_poller import EndpointPoller
from cloud_variable_ep import CloudVariableEp
from url_poller import URLPoller
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
    },
    "translations_json":{
        "url" : "https://raw.githubusercontent.com/lancaster-university/rest-radio/master/hub/translations.json",
        "poll_time" : 60
    }
}

auto_detect = False

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

while(True):

    # if the bridged micro:bit has sent us data, process
    if serial_handler.buffered() > 0:
        rPacket = RadioPacket(serial_handler.read_packet())
        requestHandler = RequestHandler(rPacket,translations, hub_variables, None)
        bytes = requestHandler.handleRequest()
        serial_handler.write_packet(bytes)

    # every few minutes we check github for new translations.
    if github_poller.poll():
        print "Updating translations from Github"
        translations = github_poller.get_cached()
        with open("./translations-remote.json", 'w') as f:
            f.write(json.dumps(github_poller.get_cached(), indent=4, sort_keys=True))

    # prevent burning the processor :)
    sleep(0.01)