#ifndef RADIO_REST_H
#define RADIO_REST_H

#include "Radio.h"
#include "DynamicType.h"
#include "MicroBitConfig.h"

#define RADIO_REST_ID                       62965
#define REST_HEADER_SIZE                    6
#define REST_RADIO_MAXIMUM_TX_BUFFERS       10
#define REST_RADIO_MAXIMUM_RX_BUFFERS       10
#define MAX_PAYLOAD_SIZE                    (254 - 4 - REST_HEADER_SIZE)

#define REST_RADIO_NO_RESPONSE_THRESHOLD    30

#define REQUEST_TYPE_GET_REQUEST            0x01
#define REQUEST_TYPE_PUT_REQUEST            0x02
#define REQUEST_TYPE_POST_REQUEST           0x04
#define REQUEST_TYPE_DELETE_REQUEST         0x08

#define REQUEST_TYPE_STATUS_ACK             0x10
#define REQUEST_TYPE_STATUS_ERROR           0x20
#define REQUEST_TYPE_STATUS_OK              0x40
#define REQUEST_TYPE_REPEATING              0x80

struct DataPacket
{
    uint16_t id;
    uint16_t app_id;
    uint8_t request_type;
    uint8_t subtype; // lower four bits are typing, upper four bits are data size
    uint8_t payload[MAX_PAYLOAD_SIZE];

    uint16_t len;
    int16_t no_response_count;
    DataPacket* next;
} __attribute((packed));

class RadioREST : public MicroBitComponent
{
    uint16_t appId;
    Radio& radio;

    DataPacket* txQueue;
    DataPacket* rxQueue;

    int addToQueue(DataPacket** queue, DataPacket* packet);
    DataPacket* removeFromQueue(DataPacket** queue, uint16_t id);
    DataPacket* composePacket(uint8_t type, uint8_t subtype, uint8_t* payload, uint8_t payload_len, uint16_t app_id, uint16_t packet_id = 0);
    void sendDataPacket(DataPacket* p);

    public:

    RadioREST(Radio& r, uint16_t appId);

    int send(DataPacket* p);

    DynamicType getRequest(ManagedString url, bool repeating = false);

    uint16_t getRequestAsync(ManagedString url, bool repeating = false);

    void packetReceived();

    virtual void idleTick();

    DynamicType recv(uint16_t id);

    DataPacket* recvRaw(uint16_t id);

    // ManagedBuffer putRequest(ManagedString url);

    // ManagedBuffer postRequest(ManagedString url);

    // ManagedBuffer deleteRequest(ManagedString url);
};


#endif