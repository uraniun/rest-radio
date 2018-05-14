#include "Radio.h"
#include "RadioREST.h"
#include "MicroBitFiber.h"

extern void log_string(const char *);
extern void log_num(int num);

RadioREST::RadioREST(Radio& r, uint16_t appId) : radio(r)
{
    this->appId = appId;
    this->txQueue = NULL;
    this->rxQueue = NULL;

    fiber_add_idle_component(this);
}

DataPacket* RadioREST::removeFromQueue(DataPacket** queue, uint16_t id)
{
    DataPacket *p = *queue;
    DataPacket *previous = *queue;

    log_string("start");
    log_num(id);

    while (p != NULL)
    {
        log_string("iter");
        log_num(p->id);
        if (id == p->id)
        {
            log_string("found");
            if (p == *queue)
                *queue = p->next;
            else
                previous->next = p->next;

            return p;
        }

        previous = p;
        p = p->next;
    }

    return NULL;
}

int RadioREST::addToQueue(DataPacket** queue, DataPacket* packet)
{
    int queueDepth = 0;

    // We add to the tail of the queue to preserve causal ordering.
    packet->next = NULL;

    if (*queue == NULL)
    {
        *queue = packet;
    }
    else
    {
        DataPacket *p = *queue;

        while (p->next != NULL)
        {
            p = p->next;
            queueDepth++;
        }

        if (queueDepth >= REST_RADIO_MAXIMUM_TX_BUFFERS)
        {
            delete packet;
            return MICROBIT_NO_RESOURCES;
        }

        p->next = packet;
    }

    return MICROBIT_OK;
}


void RadioREST::sendDataPacket(DataPacket* p)
{
    RadioFrameBuffer buf;

    buf.length = p->len + REST_HEADER_SIZE + RADIO_HEADER_SIZE - 1;
    buf.version = 1;
    buf.group = 0;
    buf.protocol = RADIO_PROTOCOL_REST;
    memcpy(buf.payload, (uint8_t*)p, p->len + REST_HEADER_SIZE);

    radio.send(&buf);
}

DataPacket* RadioREST::composePacket(uint8_t type, uint8_t* payload, uint8_t payload_len, uint16_t app_id, uint16_t packet_id)
{
    uint32_t id = (packet_id != 0) ? packet_id : microbit_random(65535);

    DataPacket* p = new DataPacket();
    p->app_id = app_id;
    p->id = id;
    p->request_type = type;

    uint32_t len = min(MAX_PAYLOAD_SIZE, payload_len);

    p->len = len;

    // we don't always have any payload, like for ACKs.
    if (len > 0)
        memcpy(p->payload, payload, len);

    return p;
}

int RadioREST::send(DataPacket* p)
{
    sendDataPacket(p);
    addToQueue(&txQueue, p);
    return MICROBIT_OK;
}

DynamicType RadioREST::getRequest(ManagedString url, bool repeating)
{
    // + 2 for null terminator and type byte
    uint8_t bufLen = url.length() + 2;
    uint8_t* urlBuf = (uint8_t *)malloc(bufLen);
    urlBuf[0] |= SUBTYPE_STRING;
    memcpy(urlBuf + 1,url.toCharArray(), bufLen - 1);

    DataPacket *p = composePacket(REQUEST_TYPE_GET_REQUEST | ((repeating) ? REQUEST_TYPE_REPEATING : 0), urlBuf, bufLen, appId);
    uint32_t id = p->id;
    sendDataPacket(p);
    addToQueue(&txQueue, p);

    fiber_wake_on_event(RADIO_REST_ID, id);
    schedule();
    return recv(id);
}

// returns the message bus value to use
uint16_t RadioREST::getRequestAsync(ManagedString url, bool repeating)
{
    // + 2 for null terminator and type byte
    uint8_t bufLen = url.length() + 2;
    uint8_t* urlBuf = (uint8_t *)malloc(bufLen);
    urlBuf[0] |= SUBTYPE_STRING;
    memcpy(urlBuf + 1,url.toCharArray(), bufLen - 1);

    DataPacket *p = composePacket(REQUEST_TYPE_GET_REQUEST | ((repeating) ? REQUEST_TYPE_REPEATING : 0), urlBuf, bufLen, appId);
    uint32_t id = p->id;

    sendDataPacket(p);
    addToQueue(&txQueue, p);
    return id;
}

DynamicType RadioREST::postRequest(ManagedString url, DynamicType& parameters)
{
    uint16_t strLen = url.length() + 1; // for null terminator

    uint16_t bufLen = strLen + 1 + parameters.length(); // + 1 for subtype byte
    uint8_t* urlBuf = (uint8_t *)malloc(bufLen);
    urlBuf[0] = SUBTYPE_STRING;

    memcpy(urlBuf + 1,url.toCharArray(), strLen);
    memcpy(urlBuf + 1 + strLen, parameters.getBytes(), parameters.length());

    DataPacket *p = composePacket(REQUEST_TYPE_POST_REQUEST, urlBuf, bufLen, appId);
    uint32_t id = p->id;
    sendDataPacket(p);
    addToQueue(&txQueue, p);
    // should be wake on event?
    fiber_wake_on_event(RADIO_REST_ID, id);
    schedule();
    return recv(id);
}

uint16_t RadioREST::postRequestAsync(ManagedString url, DynamicType& parameters)
{
    uint16_t strLen = url.length() + 1; // for null terminator

    uint16_t bufLen = strLen + 1 + parameters.length(); // + 1 for subtype byte
    uint8_t* urlBuf = (uint8_t *)malloc(bufLen);
    urlBuf[0] |= SUBTYPE_STRING;
    memcpy(urlBuf + 1,url.toCharArray(), url.length() + 1);

    memcpy(urlBuf + 1 + strLen, parameters.getBytes(), parameters.length());

    DataPacket *p = composePacket(REQUEST_TYPE_POST_REQUEST, urlBuf, bufLen, appId);
    uint32_t id = p->id;
    sendDataPacket(p);
    addToQueue(&txQueue, p);
    return id;
}

#define DATA_PACKET_WAITING_FOR_SEND        0x01
#define DATA_PACKET_WAITING_FOR_ACK         0x02
#define DATA_PACKET_ACK_RECEIVED            0x04

void RadioREST::idleTick()
{
    if (txQueue == NULL)
        return;

    // walk the txqueue and check to see if any have exceeded our retransmit time
    bool transmitted = false;
    bool pop = false;

    DataPacket* p = txQueue;

    while(p != NULL)
    {
        // only transmit once every idle tick
        if (p->status & DATA_PACKET_WAITING_FOR_SEND && !transmitted)
        {
            transmitted = true;
            sendDataPacket(p);
            p->status = DATA_PACKET_WAITING_FOR_ACK;
            p->no_response_count = 0;
            p->retry_count = 0;
        }
        else if (p->status & DATA_PACKET_WAITING_FOR_ACK)
        {
             p->no_response_count++;

            if (p->no_response_count > REST_RADIO_NO_RESPONSE_THRESHOLD && !transmitted)
            {
                p->retry_count++;

                if (p->retry_count > REST_RADIO_RETRY_THRESHOLD)
                    pop = true;

                sendDataPacket(p);
                p->no_response_count = 0;
                transmitted = true;
            }
        }
        else if (p->status & DATA_PACKET_ACK_RECEIVED)
        {
            p->no_response_count++;

            if (p->no_response_count > REST_RADIO_NO_RESPONSE_THRESHOLD
                pop = true;
        }

        if (pop)
        {
            pop = false;
            DataPacket *t = removeFromQueue(&txQueue, p->id);

            t->request_type = REQUEST_TYPE_STATUS_ERROR;

            addToQueue(&rxQueue, t);

            MicroBitEvent(RADIO_REST_ID, p->id);
        }

        p = p->next;
    }
}

/**
  * Protocol handler callback. This is called when the radio receives a packet marked as a datagram.
  *
  * This function process this packet, and queues it for user reception.
  */
void RadioREST::packetReceived()
{
    RadioFrameBuffer* packet = radio.recv();
    DataPacket* temp = (DataPacket*)packet->payload;

    log_string("RX: ");
    log_num((int) this->appId);
    log_num((int) temp->app_id);

    // ignore any packets that aren't part of our application
    if (appId != 0 && temp->app_id != this->appId)
    {
        log_string("IGNORED");
        delete packet;
        return;
    }

    // if it's only an ACK, we can remove from our txQueue, and return.
    if (temp->request_type & REQUEST_TYPE_STATUS_ACK)
    {
        log_string("REMOVING");
        DataPacket *t = removeFromQueue(&txQueue, temp->id);
        log_num((int)t);
        if (t)
            delete t;
        delete packet;
        return;
    }

    log_string("AFTER");

    // add to our RX queue for app handling.
    DataPacket* p = new DataPacket();
    memcpy(p, packet->payload, packet->length - (RADIO_HEADER_SIZE - 1));
    p->len = packet->length - (RADIO_HEADER_SIZE - 1);

    delete packet;

    p->no_response_count = 0;
    p->next = NULL;

    addToQueue(&rxQueue, p);

    // send an ACK.
    DataPacket *ack = composePacket(REQUEST_TYPE_STATUS_ACK, NULL, 0, p->app_id, p->id);
    sendDataPacket(ack);
    log_string("ACK");

    delete ack;

    // wake any waiting fibers.
    MicroBitEvent(RADIO_REST_ID, p->id);
}

DynamicType RadioREST::recv(uint16_t id)
{
    DataPacket *t = removeFromQueue(&rxQueue, id);

    if (t == NULL)
        return DynamicType();
    
    log_string("VALID\r\n");
    log_num(t->len);
    log_num(t->len - REST_HEADER_SIZE);

    DynamicType dt(t->len - REST_HEADER_SIZE, t->payload);

    delete t;

    return dt;
}

DataPacket* RadioREST::recvRaw(uint16_t id)
{
    return removeFromQueue(&rxQueue, id);
}