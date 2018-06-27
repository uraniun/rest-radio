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
    ManagedString setBulbVal(ManagedString bulbName, int level);
    ManagedString setBulbColour(ManagedString bulbName, int colour);

    ManagedString getSwitchState(ManagedString endpoint);
    ManagedString getBulbState(ManagedString endpoint);
    ManagedString getSensorState(ManagedString endpoint);
    ManagedString getBulbLevel(ManagedString endpoint);
    ManagedString getBulbColour(ManagedString endpoint);

    
};

#endif