#ifndef SHARESERVICE_SERVICE_H
#define SHARESERVICE_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"



class ShareService : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    

    public:

    virtual void idleTick();

    ShareService(MicroBitPeridoRadio& r);

    ManagedString setShareHistoricalData(ManagedString value, ManagedString name ,ManagedString space, ManagedString unit);

    ManagedString setShareData(ManagedString value, ManagedString name, int level);

    ManagedString getFetchData(ManagedString endpoint);

    
};

#endif