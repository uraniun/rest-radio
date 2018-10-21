#include "IotService.h"

IotService::IotService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void IotService::idleTick()
{
    
}

ManagedString IotService::setSwitchState(ManagedString switchName, int state) {
    DynamicType t;
    t.appendString(switchName);
    t.appendInteger(state);
    DynamicType res = radio.cloud.rest.postRequest("/iot/switchState/", t);
    return res.getString(0);
}
ManagedString IotService::setBulbState(ManagedString bulbName, int state) {
    DynamicType t;
    t.appendString(bulbName);
    t.appendInteger(state);
    DynamicType res = radio.cloud.rest.postRequest("/iot/bulbState/", t);
    return res.getString(0);
}
ManagedString IotService::setBulbTemp(ManagedString bulbName, int colour) {
    DynamicType t;
    t.appendString(bulbName);
    t.appendInteger(colour);
    DynamicType res = radio.cloud.rest.postRequest("/iot/bulbTemp/", t);
    return res.getString(0);
}
ManagedString IotService::setBulbLevel(ManagedString bulbName, int level) {
    DynamicType t;
    t.appendString(bulbName);
    t.appendInteger(level);
    DynamicType res = radio.cloud.rest.postRequest("/iot/bulbLevel/", t);
    return res.getString(0);
}
ManagedString IotService::setBulbColour(ManagedString bulbName, int colour) {
    DynamicType t;
    t.appendString(bulbName);
    t.appendInteger(colour);
    DynamicType res = radio.cloud.rest.postRequest("/iot/bulbColour/", t);
    return res.getString(0);
}
ManagedString IotService::getBulbState(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getBulbTemp(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getSensorState(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getSwitchState(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getBulbLevel(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getBulbColour(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IotService::getSensorTemp(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iot/" + endpoint + "/");
    return res.getString(0);
}
