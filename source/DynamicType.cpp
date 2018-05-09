#include "DynamicType.h"
#include "ErrorNo.h"

void DynamicType::init(uint8_t len, uint8_t* payload, uint8_t subtype)
{
    ptr = (SubTyped *) malloc(sizeof(SubTyped) + len);
    ptr->init();

    ptr->len = len;
    ptr->subtype = subtype;

    // Copy in the data buffer, if provided.
    if (len > 0)
        memcpy(ptr->payload, payload, len);
}

DynamicType::DynamicType()
{
    this->init(0, NULL, 0);
}

DynamicType::DynamicType(uint8_t len, uint8_t* payload, uint8_t subtype)
{
    this->init(len, payload, subtype);
}

DynamicType::DynamicType(const DynamicType &buffer)
{
    ptr = buffer.ptr;
    ptr->incr();
}

DynamicType::~DynamicType()
{
    ptr->decr();
}

DynamicType& DynamicType::operator = (const DynamicType &p)
{
    if(ptr == p.ptr)
        return *this;

    ptr->decr();
    ptr = p.ptr;
    ptr->incr();

    return *this;
}

uint8_t* DynamicType::getBytes()
{
    return ptr->payload;
}

int DynamicType::length()
{
    return ptr->len;
}

ManagedString DynamicType::getString(int index)
{
    if (index < 0 || !(ptr->subtype & SUBTYPE_STRING))
        return MICROBIT_INVALID_PARAMETER;

    if (index > 0 && !(ptr->subtype & SUBTYPE_ARRAY))
        return ManagedString();

    if (index == 0)
        return ManagedString((char*)ptr->payload);

    int strCount = 0;
    int iterator = 0;

    uint8_t* p = ptr->payload;

    while (iterator < ptr->len)
    {
        if(*p == 0)
            strCount++;

        p++;
        iterator++;

        if (strCount == index)
            return ManagedString((char*) ptr->payload + iterator);
    }

    return ManagedString();
}

int DynamicType::getNumber(int index)
{
    if (index < 0 || !(ptr->subtype & SUBTYPE_NUMBER))
        return MICROBIT_INVALID_PARAMETER;

    if (index > 0 && !(ptr->subtype & SUBTYPE_ARRAY))
        return MICROBIT_INVALID_PARAMETER;

    if (index > (ptr->len / sizeof(int)))
        return MICROBIT_INVALID_PARAMETER;

    if (index == 0)
        return ptr->payload[0];

    int* p = (int*)ptr->payload;
    return p[index];
}

int DynamicType::appendString()
{
    return MICROBIT_OK;
}

int DynamicType::appendNumber()
{
    return MICROBIT_OK;
}
