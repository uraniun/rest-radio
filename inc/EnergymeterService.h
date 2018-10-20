#ifndef ENERGYMETERSERVICE_SERVICE_H
#define ENERGYMETERSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class EnergymeterService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    EnergymeterService(Radio& r);

    int sendEnergyLevel(ManagedString name, int value, int type);

    
};

#endif