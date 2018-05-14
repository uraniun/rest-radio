from serial import Serial
import sys, struct, json, re
from weather import Weather, Unit
from radio_packet import RadioPacket
from request_handler import RequestHandler


# constants for the serial line internet protocol.
SLIP_END = chr(0xC0)
SLIP_ESC = chr(0xDB)
SLIP_ESC_END = chr(0xDC)
SLIP_ESC_ESC = chr(0xDD)

# struct DataPacket
# {
#     uint16_t id;
#     uint16_t app_id;
#     uint8_t request_type;
#     uint8_t subtype; // lower four bits are typing, upper four bits are data size
#     uint8_t payload[MAX_PAYLOAD_SIZE];
# }

def error(originalPacket, serial):
    returnPacket = RadioPacket(originalPacket)
    serial.write(returnPacket.marshall(False))


s = Serial(port= "/dev/cu.usbmodem1462",baudrate=115200)

translations = open("./translations.json")
translations = json.load(translations)

while(True):

    c = None
    packet = []
    debug = False
    while True:
        c = s.read()

        if c == '\\':
            debug = not debug
            print "debug mode toggled", str(debug)
            continue

        if not debug:

            if c == SLIP_END:
                print "SLIP_END"
                break

            if c == SLIP_ESC:
                next = s.read()

                if next == SLIP_ESC_END:
                    packet += [SLIP_END]

                elif next == SLIP_ESC_ESC:
                    packet += [SLIP_ESC]

                else:
                    packet += [c]
                    packet += [next]

                continue

            print("%c [%d]" % (c, ord(c)))
            packet += [c]
        else:
            print("DEBUG: %c [%d]" % (c, ord(c)))

    packet = ''.join(packet)

    print "joined: %s len %d" % (packet,len(packet))
    print packet

    rPacket = RadioPacket(packet)

    requestHandler = RequestHandler(rPacket,translations)

    bytes = requestHandler.handleRequest()

    finalBytes = []

    for b in bytes:
        if b == SLIP_ESC:
            finalBytes += SLIP_ESC
            finalBytes += SLIP_ESC_ESC
            continue

        if b == SLIP_END:
            finalBytes += SLIP_ESC
            finalBytes +=SLIP_ESC_END
            continue

        finalBytes += b
    
    finalBytes += SLIP_END

    for p in finalBytes:
        print("%c [%d]" % (p, ord(p)))

    s.write(''.join(finalBytes))

    # weather = Weather(unit=Unit.CELSIUS)
    # location = weather.lookup_by_location(loc)
    # condition = location.condition

    # print condition.text

    # packed = struct.pack("<IIIs",app_id,namespace_id,len(condition.text),str(condition.text))
    # s.write(packed)


