#ifndef %SERVICE_NAME_UPPER%_SERVICE_H
#define %SERVICE_NAME_UPPER%_SERVICE_H

#include "MicroBitPeridoRadio.h"
#include "MicroBitComponent.h"

%SERVICE_STRUCTS%

class %SERVICE_NAME_PASCAL% : public MicroBitComponent
{
    MicroBitPeridoRadio& radio;

    %SERVICE_STRUCT_MEMBERS%

    public:

    virtual void idleTick();

    %SERVICE_NAME_PASCAL%(MicroBitPeridoRadio& r);

    %SERVICE_MEMBER_FUNCTION_DEFINITIONS%
};

#endif