#ifndef WEATHERSERVICE_SERVICE_H
#define WEATHERSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"

struct WeatherServiceForecastNow {
    int high;
    int low;
    ManagedString text;
};

struct WeatherServiceForecastTomorrow {
    ManagedString high;
    ManagedString low;
    ManagedString text;
};

struct WeatherServiceWind {
    ManagedString chill;
    ManagedString direction;
    ManagedString speed;
};


class WeatherService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    WeatherService(MicroBitPeridoRadio& r);

    int setRoomNone(ManagedString room, int temperature, int light_level, int humidity);
    int setRoomLightlevel(ManagedString room, int light_level);
    int setRoomTemperature(ManagedString room, int temperature);
    int setRoomHumidity(ManagedString room, int humidity);

    WeatherServiceForecastNow getForecastNow(ManagedString location);
    WeatherServiceForecastTomorrow getForecastTomorrow(ManagedString location);
    ManagedString getTemperature(ManagedString location);
    WeatherServiceWind getWind(ManagedString location);

    
};

#endif