#include "InitService.h"
#include "ErrorNo.h"

InitService::InitService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void InitService::idleTick()
{
    
}

ManagedString InitService::setReset(ManagedString reset) {
    DynamicType t;
    t.appendString(reset);
    DynamicType res = radio.cloud.rest.postRequest("/init/reset/", t);
    return res.getString(0);
}
ManagedString InitService::setSchoolId(ManagedString schoolid) {
    DynamicType t;
    t.appendString(schoolid);
    DynamicType res = radio.cloud.rest.postRequest("/init/schoolId/", t);
    return res.getString(0);
}
ManagedString InitService::setPiId(ManagedString piid) {
    DynamicType t;
    t.appendString(piid);
    DynamicType res = radio.cloud.rest.postRequest("/init/piId/", t);
    return res.getString(0);
}
