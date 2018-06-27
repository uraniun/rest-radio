#include "CarbonService.h"

CarbonService::CarbonService(Radio& r) : radio(r)
{
    
}

void CarbonService::idleTick()
{
    
}

ManagedString CarbonService::getCarbonIndex(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/carbon/" + endpoint + "/");
    return res.getString(0);
}
ManagedString CarbonService::getCarbonValue(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/carbon/" + endpoint + "/");
    return res.getString(0);
}
ManagedString CarbonService::getCarbonGenerationMix(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/carbon/" + endpoint + "/");
    return res.getString(0);
}
