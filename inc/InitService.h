#ifndef INITSERVICE_SERVICE_H
#define INITSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class InitService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    InitService(Radio& r);

    ManagedString setReset(ManagedString reset);
    ManagedString setSchoolId(ManagedString schoolid);
    ManagedString setPiId(ManagedString piid);

    
};

#endif