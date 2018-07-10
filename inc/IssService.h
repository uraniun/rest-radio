#ifndef ISSSERVICE_SERVICE_H
#define ISSSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class IssService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    IssService(Radio& r);

    ManagedString getName(ManagedString endpoint);
    ManagedString getAltitude(ManagedString endpoint);
    ManagedString getSolarlocation(ManagedString endpoint);
    ManagedString getVisibility(ManagedString endpoint);
    ManagedString getDaynum(ManagedString endpoint);
    ManagedString getLocation(ManagedString endpoint);
    ManagedString getVelocity(ManagedString endpoint);
    ManagedString getId(ManagedString endpoint);

    
};

#endif