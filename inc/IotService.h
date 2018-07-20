#ifndef IOTSERVICE_SERVICE_H
#define IOTSERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class IotService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    IotService(Radio& r);

    ManagedString setSwitchState(ManagedString switchName, int state);
    ManagedString setBulbState(ManagedString bulbName, int state);
    ManagedString setBulbTemp(ManagedString bulbName, int colour);
    ManagedString setBulbLevel(ManagedString bulbName, int level);
    ManagedString setBulbColour(ManagedString bulbName, int colour);

    ManagedString getBulbState(ManagedString endpoint);
    ManagedString getBulbTemp(ManagedString endpoint);
    ManagedString getSensorState(ManagedString endpoint);
    ManagedString getSwitchState(ManagedString endpoint);
    ManagedString getBulbLevel(ManagedString endpoint);
    ManagedString getBulbColour(ManagedString endpoint);
    ManagedString getSensorTemp(ManagedString endpoint);

    
};

#endif