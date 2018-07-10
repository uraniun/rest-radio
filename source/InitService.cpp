#include "InitService.h"

InitService::InitService(Radio& r) : radio(r)
{
    
}

void InitService::idleTick()
{
    
}

int InitService::setReset(ManagedString reset) {
    DynamicType t;
    t.appendString(reset);
    DynamicType res = radio.cloud.rest.postRequest("/init/reset/", t);
    return res.getStatus();
}
int InitService::setSchoolId(ManagedString schoolid) {
    DynamicType t;
    t.appendString(schoolid);
    DynamicType res = radio.cloud.rest.postRequest("/init/schoolId/", t);
    return res.getStatus();
}
int InitService::setPiId(ManagedString piid) {
    DynamicType t;
    t.appendString(piid);
    DynamicType res = radio.cloud.rest.postRequest("/init/piId/", t);
    return res.getStatus();
}
