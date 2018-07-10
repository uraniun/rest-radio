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
    int getAltitude(ManagedString endpoint);
    ManagedString getSolarlocation(ManagedString endpoint);
    ManagedString getVisibility(ManagedString endpoint);
    int getDaynum(ManagedString endpoint);
    ManagedString getLocation(ManagedString endpoint);
    int getVelocity(ManagedString endpoint);
    int getId(ManagedString endpoint);

    
};

#endif