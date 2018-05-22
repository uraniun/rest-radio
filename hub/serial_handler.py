from serial import Serial
from radio_packet import RadioPacket
import struct

# constants for the serial line internet protocol.
SLIP_END = chr(0xC0)
SLIP_ESC = chr(0xDB)
SLIP_ESC_END = chr(0xDC)
SLIP_ESC_ESC = chr(0xDD)

class SerialHandler():

    s = None

    def __init__(self, path, baud= 115200):
        self.s = Serial(port= path,baudrate=baud)

    def error(self, originalPacket):
        returnPacket = RadioPacket(originalPacket)
        self.s.write(returnPacket.marshall(False))

    def buffered(self):
        return self.s.in_waiting

    def read_packet(self):
        c = None
        packet = []
        debug = False

        while True:
            c = self.s.read()

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

        return ''.join(packet)

    def write_packet(self, bytes):
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

        self.s.write(''.join(finalBytes))