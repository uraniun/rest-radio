#ifndef SHARESERVICE_SERVICE_H
#define SHARESERVICE_SERVICE_H

#include "Radio.h"
#include "MicroBitComponent.h"



class ShareService : public MicroBitComponent
{
    Radio& radio;

    

    public:

    virtual void idleTick();

    ShareService(Radio& r);

    int setSchool(ManagedString variable_name, ManagedString value);
    int setSchool(ManagedString variable_name, int value);
    int setSchool(ManagedString variable_name, float value);
    int setEveryone(ManagedString variable_name, ManagedString value);
    int setEveryone(ManagedString variable_name, int value);
    int setEveryone(ManagedString variable_name, float value);

    
};

#endif