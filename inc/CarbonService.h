#ifndef CARBONSERVICE_SERVICE_H
#define CARBONSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class CarbonService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    CarbonService(MicroBitPeridoRadio& r);

    ManagedString getCarbonIndex(ManagedString endpoint);
    ManagedString getCarbonValue(ManagedString endpoint);
    ManagedString getCarbonGenerationMix(ManagedString endpoint);

    
};

#endif