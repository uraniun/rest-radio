#include "ShareService.h"

ShareService::ShareService(Radio& r) : radio(r)
{
    
}

void ShareService::idleTick()
{
    
}

int ShareService::setSchool(ManagedString variable_name, ManagedString value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendString(value);
    DynamicType res = radio.rest.postRequest("/share/school//", t);
    return res.getStatus();
}
int ShareService::setSchool(ManagedString variable_name, int value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendInteger(value);
    DynamicType res = radio.rest.postRequest("/share/school//", t);
    return res.getStatus();
}
int ShareService::setSchool(ManagedString variable_name, float value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendFloat(value);
    DynamicType res = radio.rest.postRequest("/share/school//", t);
    return res.getStatus();
}
int ShareService::setEveryone(ManagedString variable_name, ManagedString value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendString(value);
    DynamicType res = radio.rest.postRequest("/share/everyone//", t);
    return res.getStatus();
}
int ShareService::setEveryone(ManagedString variable_name, int value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendInteger(value);
    DynamicType res = radio.rest.postRequest("/share/everyone//", t);
    return res.getStatus();
}
int ShareService::setEveryone(ManagedString variable_name, float value) {
    DynamicType t;
    t.appendString(variable_name);
    t.appendFloat(value);
    DynamicType res = radio.rest.postRequest("/share/everyone//", t);
    return res.getStatus();
}
