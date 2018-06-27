#include "WeatherService.h"

WeatherService::WeatherService(Radio& r) : radio(r)
{
    
}

void WeatherService::idleTick()
{
    
}

int WeatherService::setRoomNone(ManagedString room, int temperature, int light_level, int humidity) {
    DynamicType t;
    t.appendInteger(temperature);
    t.appendInteger(light_level);
    t.appendInteger(humidity);
    DynamicType res = radio.cloud.rest.postRequest("/weather/" + room + "/", t);
    return res.getStatus();
}
int WeatherService::setRoomLightlevel(ManagedString room, int light_level) {
    DynamicType t;
    t.appendInteger(light_level);
    DynamicType res = radio.cloud.rest.postRequest("/weather/" + room + "/lightlevel/", t);
    return res.getStatus();
}
int WeatherService::setRoomTemperature(ManagedString room, int temperature) {
    DynamicType t;
    t.appendInteger(temperature);
    DynamicType res = radio.cloud.rest.postRequest("/weather/" + room + "/temperature/", t);
    return res.getStatus();
}
int WeatherService::setRoomHumidity(ManagedString room, int humidity) {
    DynamicType t;
    t.appendInteger(humidity);
    DynamicType res = radio.cloud.rest.postRequest("/weather/" + room + "/humidity/", t);
    return res.getStatus();
}
WeatherServiceForecastNow WeatherService::getForecastNow(ManagedString location) {
    DynamicType res = radio.cloud.rest.getRequest("/weather/" + location + "/forecastNow/");
    WeatherServiceForecastNow ret;
    if (res.getStatus() == MICROBIT_OK) {
        ret.high = res.getInteger(0);
        ret.low = res.getInteger(1);
        ret.text = res.getString(2);
    }
    return ret;
}
WeatherServiceForecastTomorrow WeatherService::getForecastTomorrow(ManagedString location) {
    DynamicType res = radio.cloud.rest.getRequest("/weather/" + location + "/forecastTomorrow/");
    WeatherServiceForecastTomorrow ret;
    if (res.getStatus() == MICROBIT_OK) {
        ret.high = res.getString(0);
        ret.low = res.getString(1);
        ret.text = res.getString(2);
    }
    return ret;
}
ManagedString WeatherService::getTemperature(ManagedString location) {
    DynamicType res = radio.cloud.rest.getRequest("/weather/" + location + "/temperature/");
    return res.getString(0);
}
WeatherServiceWind WeatherService::getWind(ManagedString location) {
    DynamicType res = radio.cloud.rest.getRequest("/weather/" + location + "/wind/");
    WeatherServiceWind ret;
    if (res.getStatus() == MICROBIT_OK) {
        ret.chill = res.getString(0);
        ret.direction = res.getString(1);
        ret.speed = res.getString(2);
    }
    return ret;
}
