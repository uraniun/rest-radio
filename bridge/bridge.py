from serial import Serial
import sys, struct, json, re, urllib2, requests,urllib
from weather import Weather, Unit
from radio_packet import RadioPacket


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

def recursive_find(parts, json):
    if parts == []:
        return json

    if len(parts) == 1:
        head, rest = parts[0],[]
    else:
        head, rest = parts[0], parts[1:]

    if head not in json.keys():
        return {}

    return recursive_find(rest,json[head])

def error(originalPacket, serial):
    returnPacket = RadioPacket(originalPacket)
    serial.write(returnPacket.marshall(False))


s = Serial(port= "/dev/cu.usbmodem1462",baudrate=115200)

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

    with open("./translations.json", "r") as f:
        translations = json.load(f)

        out = {}

        url = rPacket.get(0)

        pieces = url.split("/")

        part, rest = pieces[0],pieces[1:]

        translation = translations[part]

        part, rest = rest[0],rest[1:]

        operation = translation["GET"]
        baseURL = operation["baseURL"]
        queryObject = operation["queryObject"]
        urlFormat = [x for x in operation["microbitQueryString"].split("/") if x]

        for format in urlFormat:
            name = re.search("%(.*)%",format)
            key = name.group(1)

            if key[-1] == "?":
                if part == None:
                    break

                key = key[:-1]

            out[key] = part

            # the line below won't work if rest is empty...
            if len(rest) == 0:
                part = None
                continue

            part, rest = rest[0], rest[1:]

        filler = {}

        for param in queryObject:
            res = re.findall(r"(%([a-zA-z]*)(?:\?=)?([a-z]*)%)",queryObject[param])
            filler[param] = res

        for fillerKey in filler:
            for tup in filler[fillerKey]:
                match, key, default = tup

                value = None

                if key in out.keys():
                    value = out[key]
                elif default:
                    value = default
                else:
                    raise Exception("No value specified for " + key)

                queryObject[fillerKey] = queryObject[fillerKey].replace(match,value)

        r = requests.get(baseURL, params=queryObject)

        print out.keys()
        print out["endpoint"]
        print operation["endpoint"].keys()

        if out["endpoint"] not in operation["endpoint"].keys():
            raise Exception("endpoint not present in microbit query string")

        endpoint = operation["endpoint"][out["endpoint"]]

        path = [x for x in endpoint["jsonPath"].split(".") if x]

        response = json.loads(r.text)

        jsonObj = recursive_find(path, response)

        returnPacket = RadioPacket(rPacket)

        returnVariables = endpoint["returns"]

        for ret in returnVariables:
            print jsonObj[ret["name"]]
            returnPacket.append(jsonObj[ret["name"]])

        bytes = returnPacket.marshall(True)

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


