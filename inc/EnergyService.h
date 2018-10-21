#ifndef ENERGYSERVICE_SERVICE_H
#define ENERGYSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class EnergyService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    EnergyService(MicroBitPeridoRadio& r);

    ManagedString getEnergyLevel(ManagedString endpoint);

    
};

#endif