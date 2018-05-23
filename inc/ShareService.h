#ifndef SHARESERVICE_SERVICE_H
#define SHARESERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class ShareService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    ShareService(Radio& r);

    int setSchool(uint16_t name_hash, ManagedString value);
    int setSchool(uint16_t name_hash, int value);
    int setSchool(uint16_t name_hash, float value);
    int setEveryone(uint16_t name_hash, ManagedString value);
    int setEveryone(uint16_t name_hash, int value);
    int setEveryone(uint16_t name_hash, float value);

    
};

#endif