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

    int setSchoolId(ManagedString schoolid);
    int setPiId(ManagedString piid);

    
};

#endif