#ifndef CLOUD_VARIABLE_H
#define CLOUD_VARIABLE_H

#include "Radio.h"
#include "MicroBitComponent.h"
#include "ShareService.h"
#include "ManagedString.h"


class CloudVariable
{
    uint16_t variableNameHash;
    uint16_t namespace_type;
    ManagedString value;

    ShareService& share;

    uint16_t pearsonHash(ManagedString s);

    public:

    CloudVariable(ManagedString variableNamespace, ManagedString variableName, ShareService s);
};

#endif

