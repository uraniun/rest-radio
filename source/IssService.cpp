#include "IssService.h"

IssService::IssService(Radio& r) : radio(r)
{
    
}

void IssService::idleTick()
{
    
}

ManagedString IssService::getName(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getAltitude(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getSolarlocation(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getDaynumber(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getLocation(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getVisability(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getVelocity(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
ManagedString IssService::getId(ManagedString endpoint) {
    DynamicType res = radio.cloud.rest.getRequest("/iss/" + endpoint + "/");
    return res.getString(0);
}
