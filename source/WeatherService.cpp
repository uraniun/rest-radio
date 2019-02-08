#include "WeatherService.h"
#include "ErrorNo.h"

WeatherService::WeatherService(MicroBitPeridoRadio& r) : radio(r)
{
    
}

void WeatherService::idleTick()
{
    
}

ManagedString WeatherService::getForecastNow(int locationType, ManagedString location) {
    DynamicType t;
    t.appendInteger(locationType);
    t.appendString(location);
    DynamicType res = radio.cloud.rest.postRequest("/weather/forecastNow/", t);
    return res.getString(0);
}
ManagedString WeatherService::getForecastTomorrow(int locationType, ManagedString location) {
    DynamicType t;
    t.appendInteger(locationType);
    t.appendString(location);
    DynamicType res = radio.cloud.rest.postRequest("/weather/forecastTomorrow/", t);
    return res.getString(0);
}
ManagedString WeatherService::getTemperature(int locationType, ManagedString location) {
    DynamicType t;
    t.appendInteger(locationType);
    t.appendString(location);
    DynamicType res = radio.cloud.rest.postRequest("/weather/temperature/", t);
    return res.getString(0);
}
ManagedString WeatherService::getWind(int locationType, ManagedString location) {
    DynamicType t;
    t.appendInteger(locationType);
    t.appendString(location);
    DynamicType res = radio.cloud.rest.postRequest("/weather/wind/", t);
    return res.getString(0);
}
