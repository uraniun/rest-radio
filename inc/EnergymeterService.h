#ifndef ENERGYMETERSERVICE_SERVICE_H
#define ENERGYMETERSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class EnergymeterService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    EnergymeterService(MicroBitPeridoRadio& r);

    int sendEnergyLevel(ManagedString name, int value, int type);

    
};

#endif