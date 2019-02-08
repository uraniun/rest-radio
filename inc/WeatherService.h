#ifndef WEATHERSERVICE_SERVICE_H
#define WEATHERSERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class WeatherService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    WeatherService(MicroBitPeridoRadio& r);

    ManagedString getForecastNow(int locationType, ManagedString location);
    ManagedString getForecastTomorrow(int locationType, ManagedString location);
    ManagedString getTemperature(int locationType, ManagedString location);
    ManagedString getWind(int locationType, ManagedString location);

    
};

#endif