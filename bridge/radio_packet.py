import sys, struct

struct_format = "<HHb"
header_len = 5

class RadioPacket:

    SUBTYPE_STRING = 0x01
    SUBTYPE_INT = 0x02
    SUBTYPE_FLOAT = 0x04
    SUBTYPE_EVENT = 0x08

    REQUEST_TYPE_GET_REQUEST = 0x01
    REQUEST_TYPE_PUT_REQUEST = 0x02
    REQUEST_TYPE_POST_REQUEST = 0x04
    REQUEST_TYPE_DELETE_REQUEST = 0x08

    REQUEST_TYPE_STATUS_ACK = 0x10
    REQUEST_TYPE_STATUS_ERROR = 0x20
    REQUEST_TYPE_STATUS_OK = 0x40
    REQUEST_TYPE_REPEATING = 0x80

    def __init_with_class(self,radioPacket):
        self.uid = radioPacket.uid
        self.app_id = radioPacket.app_id
        self.request_type = radioPacket.request_type

    def __init_with_packet(self,packet):
        header = packet[:header_len]
        payload = packet[header_len:]

        uid, app_id, request_type = struct.unpack_from(struct_format, header)
        self.uid = uid
        self.app_id = app_id
        self.request_type = request_type

        print("uid: %d appid: %d rt: %d"%(uid, app_id,request_type))

        self.unmarshall(payload)

    def __init__(self, packet):
        self.data = []

        if packet.__class__.__name__ == "RadioPacket":
            print "init with class"
            self.__init_with_class(packet)
        else:
            print "init with packet"
            self.__init_with_packet(packet)

    def unmarshall(self, payload):

        if len(payload) == 0:
            return

        subtype, remainder = struct.unpack_from('b',payload[0])[0], payload[1:]

        print str(subtype)

        data = None
        offset = 0

        if subtype & RadioPacket.SUBTYPE_STRING:
            data = ""
            for p in remainder:
                if p == '\0':
                    break
                data += p

            offset = len(data) + 1
        elif subtype & RadioPacket.SUBTYPE_INTEGER:
           data = struct.unpack_from("i",remainder)
           offset = 4

        elif subtype & RadioPacket.SUBTYPE_FLOAT:
           data = struct.unpack_from("f",remainder)
           offset = 4

        self.data += [data]
        
        self.unmarshall(remainder[offset:])

    def marshall(self, status):
        return_code = RadioPacket.REQUEST_TYPE_STATUS_OK 
        
        if not status:
            return_code = RadioPacket.REQUEST_TYPE_STATUS_ERROR

        header = struct.pack(struct_format, self.uid, self.app_id, self.request_type | return_code)

        payload = ""

        for d in self.data:
            print str(d)

            if isinstance(d,basestring):
                payload += struct.pack("b" + str(len(d) + 1) + "s", RadioPacket.SUBTYPE_STRING,(d + "\0").encode('utf8'))

            if isinstance(d,int):
                payload += struct.pack("bi",RadioPacket.SUBTYPE_INTEGER, d)
            
            if isinstance(d,float):
                payload += struct.pack("bf", RadioPacket.SUBTYPE_FLOAT, d)

        return header + payload

    def append(self, data):
        if isinstance(data, list):
            self.data += data
        else:
            self.data += [data]

    def get(self, index):
        print self.data
        print len(self.data)
        if index >= len (self.data):
            return None

        return self.data[index]
