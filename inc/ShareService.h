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

    ManagedString setShareData(ManagedString value, ManagedString name, int level);

    ManagedString getFetchData(ManagedString endpoint);

    
};

#endif