import sys, struct, random

struct_format = "<BBHB"
header_len = 5

class RadioPacket:

    SUBTYPE_STRING = 0x01
    SUBTYPE_INT = 0x02
    SUBTYPE_FLOAT = 0x04
    SUBTYPE_EVENT = 0x08

    REQUEST_TYPE_GET_REQUEST = 0x01
    REQUEST_TYPE_POST_REQUEST = 0x02
    REQUEST_TYPE_CLOUD_VARIABLE = 0x04
    REQUEST_TYPE_BROADCAST = 0x08
    REQUEST_TYPE_HELLO = 0x10

    REQUEST_STATUS_ACK = 0x20
    REQUEST_STATUS_ERROR = 0x40
    REQUEST_STATUS_OK = 0x80

    """
    Instantiate with another RadioPacket instance
    """
    def __init_with_class(self,radioPacket):
        self.app_id = radioPacket.app_id
        self.namespace_id = radioPacket.namespace_id
        self.uid = radioPacket.uid
        self.request_type = radioPacket.request_type

    """
    Instantiate with bytes from the serial line
    """
    def __init_with_packet(self,packet):
        header = packet[:header_len]
        payload = packet[header_len:]

        app_id, namespace_id, uid, request_type = struct.unpack_from(struct_format, header)
        self.app_id = app_id
        self.namespace_id = namespace_id
        self.uid = uid
        self.request_type = request_type

        print("uid: %d appid: %d namespaceid: %d rt: %d" % (uid, app_id, namespace_id, request_type))

        for b in payload:
            print "%c[%d]" % (b , ord(b))

        self.unmarshall(payload)

    """
    Constructor

    Packet could be another radio packet instance, or a byte array.

    Alternately, if packet is none, appId uid and rtype can be manually specified.
    """
    def __init__(self, packet, appId = None, uid = None, rtype = None):
        self.data = []

        if packet.__class__.__name__ == "RadioPacket":
            print "init with class"
            self.__init_with_class(packet)
        elif packet != None:
            print "init with packet"
            self.__init_with_packet(packet)
        else:
            if appId == None or uid == None or rtype == None:
                raise Exception("unexpected type given")
            self.app_id = appId
            self.request_type = rtype
            self.uid = uid

    """
    Converts a byte string into member variables used in this instance
    """
    def unmarshall(self, payload):

        print "remaining len: %d" % (len(payload))

        if len(payload) == 0:
            return

        subtype, remainder = struct.unpack_from('b',payload[0])[0], payload[1:]

        data = None
        offset = 0

        if subtype & RadioPacket.SUBTYPE_STRING:

            data = ""
            for p in remainder:
                if p == '\0':
                    break
                data += p

            offset = len(data) + 1
            print "STRING ", str(data)

        elif subtype & RadioPacket.SUBTYPE_INT:
           data = struct.unpack_from("<i",remainder)[0]
           print "INT ", str(data)
           offset = 4

        elif subtype & RadioPacket.SUBTYPE_FLOAT:
           data = struct.unpack_from("<f",remainder)[0]
           print "FLOAT ", str(data)
           offset = 4

        self.data += [data]

        self.unmarshall(remainder[offset:])

    """
    Converts this python instance into a byte array for the serial line.

    status can be True, False, or none. True / False indicates success, or failure. None indicates no status.
    """
    def marshall(self, status = None):
        if status == None:
            return_code = 0
        elif status:
            print "MARSHALL OK"
            return_code = RadioPacket.REQUEST_STATUS_OK
        else:
            print "MARSHALL ERR"
            return_code = RadioPacket.REQUEST_STATUS_ERROR

        print("DATA:")
        print(self.data)
        print(return_code)

        header = struct.pack(struct_format, self.app_id, self.namespace_id, self.uid, self.request_type | return_code)

        payload = ""

        for d in self.data:
            print str(d)
            if isinstance(d,basestring):
                print "str"
                payload += struct.pack("<B" + str(len(d) + 1) + "s", RadioPacket.SUBTYPE_STRING,(d + "\0").encode('utf8'))

            if isinstance(d,int):
                print "INT"
                payload += struct.pack("<Bi",RadioPacket.SUBTYPE_INT, d)

            if isinstance(d,float):
                print "float"
                payload += struct.pack("<Bf", RadioPacket.SUBTYPE_FLOAT, d)

        return header + payload

    """
    append some data to this radiopacket for marshalling
    """
    def append(self, data):
        if isinstance(data, list):
            self.data += data
        else:
            self.data += [data]

    """
    Retrieve unmarshalled data.
    """
    def get(self, index):
        print self.data
        print len(self.data)
        if index >= len (self.data):
            return None

        return self.data[index]
