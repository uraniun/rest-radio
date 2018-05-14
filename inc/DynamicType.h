#ifndef DYNAMIC_TYPE_H
#define DYNAMIC_TYPE_H

#include "RefCounted.h"
#include "ManagedString.h"

#define SUBTYPE_STRING              0x01
#define SUBTYPE_INT                 0x02
#define SUBTYPE_FLOAT               0x04
#define SUBTYPE_EVENT               0x08

struct SubTyped : RefCounted
{
    uint8_t len;
    uint8_t payload[0];
};

class DynamicType
{
    SubTyped      *ptr;

    void init(uint8_t len, uint8_t* payload, bool resize = false);

    uint8_t* getPointerToIndex(int index);

    int grow(uint8_t size, uint8_t subtype, uint8_t* data);

    public:

    DynamicType(uint8_t len, uint8_t* payload);

    DynamicType(const DynamicType &buffer);

    DynamicType();

    DynamicType& operator=(const DynamicType &p);

    uint8_t* getBytes();

    int length();

    ManagedString getString(int index = 0);

    int getInteger(int index = 0);

    float getFloat(int index = 0);

    int appendString(ManagedString);

    int appendInteger(int i);

    int appendFloat(float f);

    ~DynamicType();
};

#endif