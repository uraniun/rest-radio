#ifndef DYNAMIC_TYPE_H
#define DYNAMIC_TYPE_H

#include "RefCounted.h"
#include "ManagedString.h"

#define SUBTYPE_STRING              0x01
#define SUBTYPE_NUMBER              0x02
#define SUBTYPE_EVENT               0x04
#define SUBTYPE_ARRAY               0x08

struct SubTyped : RefCounted
{
    uint8_t len;
    uint8_t subtype;
    uint8_t payload[0];
};

class DynamicType
{
    SubTyped      *ptr;

    void init(uint8_t len, uint8_t* payload, uint8_t subtype);

    public:

    DynamicType(uint8_t len, uint8_t* payload, uint8_t subtype);

    DynamicType(const DynamicType &buffer);

    DynamicType();

    DynamicType& operator=(const DynamicType &p);

    uint8_t* getBytes();

    int length();

    ManagedString getString(int index = 0);

    int getNumber(int index = 0);

    int appendString();

    int appendNumber();

    ~DynamicType();
};

#endif