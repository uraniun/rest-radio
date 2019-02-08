#include "ShareService.h"
#include "ErrorNo.h"

ShareService::ShareService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void ShareService::idleTick()
{
    
}

ManagedString ShareService::setShareData(ManagedString value, ManagedString name, int level) {
    DynamicType t;
    t.appendString(value);
    t.appendString(name);
    t.appendInteger(level);
    DynamicType res = radio.cloud.rest.postRequest("/share/shareData/", t);
    return res.getString(0);
}
ManagedString ShareService::setHistoricalData(ManagedString value, ManagedString name, ManagedString space, ManagedString unitname) {
    DynamicType t;
    t.appendString(value);
    t.appendString(name);
    t.appendString(space);
    t.appendString(unitname);
    DynamicType res = radio.cloud.rest.postRequest("/share/historicalData/", t);
    return res.getString(0);
}
ManagedString ShareService::getFetchData(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/share/" + endpoint + "/");
    return res.getString(0);
}
