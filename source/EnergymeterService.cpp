#include "EnergymeterService.h"
#include "ErrorNo.h"

EnergymeterService::EnergymeterService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void EnergymeterService::idleTick()
{
    
}

int EnergymeterService::sendEnergyLevel(ManagedString name, int value, int type) {
    DynamicType t;
    t.appendString(name);
    t.appendInteger(value);
    t.appendInteger(type);
    DynamicType res = radio.cloud.rest.postRequest("/energyMeter/energyLevel", t);
    return res.getStatus();
}
