#include "ShareService.h"

ShareService::ShareService(Radio& r) : radio(r)
{
    
}

void ShareService::idleTick()
{
    
}

int ShareService::setSchool(uint16_t name_hash, ManagedString value) {
    DynamicType t;
    t.appendString(value);
    DynamicType res = radio.rest.postRequest("/share/school/", t);
    return res.getStatus();
}
int ShareService::setSchool(uint16_t name_hash, int value) {
    DynamicType t;
    t.appendInteger(value);
    DynamicType res = radio.rest.postRequest("/share/school/", t);
    return res.getStatus();
}
int ShareService::setSchool(uint16_t name_hash, float value) {
    DynamicType t;
    t.appendFloat(value);
    DynamicType res = radio.rest.postRequest("/share/school/", t);
    return res.getStatus();
}
int ShareService::setEveryone(uint16_t name_hash, ManagedString value) {
    DynamicType t;
    t.appendString(value);
    DynamicType res = radio.rest.postRequest("/share/everyone/", t);
    return res.getStatus();
}
int ShareService::setEveryone(uint16_t name_hash, int value) {
    DynamicType t;
    t.appendInteger(value);
    DynamicType res = radio.rest.postRequest("/share/everyone/", t);
    return res.getStatus();
}
int ShareService::setEveryone(uint16_t name_hash, float value) {
    DynamicType t;
    t.appendFloat(value);
    DynamicType res = radio.rest.postRequest("/share/everyone/", t);
    return res.getStatus();
}
