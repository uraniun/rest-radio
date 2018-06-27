#include "ShareService.h"

ShareService::ShareService(Radio& r) : radio(r)
{
    
}

void ShareService::idleTick()
{
    
}

int ShareService::setShareData(ManagedString value, ManagedString name, int level) {
    DynamicType t;
    t.appendString(value);
    t.appendString(name);
    t.appendInteger(level);
    DynamicType res = radio.cloud.rest.postRequest("/share/shareData/", t);
    return res.getStatus();
}
ManagedString ShareService::getFetchData(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/share/" + endpoint + "/");
    return res.getString(0);
}
