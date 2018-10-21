#ifndef ISSSERVICE_SERVICE_H
#define ISSSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class IssService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    IssService(MicroBitPeridoRadio& r);

    ManagedString getName(ManagedString endpoint);
    int getAltitude(ManagedString endpoint);
    ManagedString getSolarlocation(ManagedString endpoint);
    ManagedString getVisibility(ManagedString endpoint);
    int getDaynum(ManagedString endpoint);
    ManagedString getLocation(ManagedString endpoint);
    int getVelocity(ManagedString endpoint);
    int getId(ManagedString endpoint);

    
};

#endif