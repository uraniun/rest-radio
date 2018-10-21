#include "EnergyService.h"
#include "ErrorNo.h"

EnergyService::EnergyService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void EnergyService::idleTick()
{
    
}

ManagedString EnergyService::getEnergyLevel(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/energy/" + endpoint + "/");
    return res.getString(0);
}
