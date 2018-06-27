#ifndef ENERGYSERVICE_SERVICE_H
#define ENERGYSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class EnergyService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    EnergyService(Radio& r);

    ManagedString getEnergyLevel(ManagedString endpoint);

    
};

#endif