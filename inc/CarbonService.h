#ifndef CARBONSERVICE_SERVICE_H
#define CARBONSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class CarbonService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    CarbonService(Radio& r);

    ManagedString getCarbonIndex(ManagedString endpoint);
    ManagedString getCarbonValue(ManagedString endpoint);
    ManagedString getCarbonGenerationMix(ManagedString endpoint);

    
};

#endif