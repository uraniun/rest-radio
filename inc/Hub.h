#ifndef HUB_H
#define HUB_H

#include "Radio.h"
#include "MicroBitSerial.h"
#include "MicroBitMessageBus.h"

class Hub
{
    Radio& radio;
    MicroBitSerial& serial;

    void onRadioPacket(MicroBitEvent e);
    void onSerialPacket(MicroBitEvent e);

    public:

    Hub(Radio& r, MicroBitSerial& s, MicroBitMessageBus& b);
};

#endif