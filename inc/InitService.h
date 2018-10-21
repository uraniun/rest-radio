#ifndef INITSERVICE_SERVICE_H
#define INITSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class InitService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    InitService(MicroBitPeridoRadio& r);

    ManagedString setReset(ManagedString reset);
    ManagedString setSchoolId(ManagedString schoolid);
    ManagedString setPiId(ManagedString piid);

    
};

#endif