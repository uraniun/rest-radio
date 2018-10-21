#include "IssService.h"

IssService::IssService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void IssService::idleTick()
{
    
}

ManagedString IssService::getName(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
int IssService::getAltitude(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getInteger(0);
}
ManagedString IssService::getSolarlocation(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getVisibility(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
int IssService::getDaynum(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getInteger(0);
}
ManagedString IssService::getLocation(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
int IssService::getVelocity(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getInteger(0);
}
int IssService::getId(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getInteger(0);
}
