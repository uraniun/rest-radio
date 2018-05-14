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

    bool searchHistory(uint16_t app_id, uint16_t id);
    void addToHistory(uint16_t app_id, uint16_t id);

    public:

    Hub(Radio& r, MicroBitSerial& s, MicroBitMessageBus& b);
};

#endif