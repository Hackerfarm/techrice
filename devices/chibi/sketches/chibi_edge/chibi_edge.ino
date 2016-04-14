/*
  Web client

 This sketch connects to a website (http://www.google.com)
 using an Arduino Wiznet Ethernet shield.

 Circuit:
 * Ethernet shield attached to pins 10, 11, 12, 13

 created 18 Dec 2009
 by David A. Mellis
 modified 9 Apr 2012
 by Tom Igoe, based on work by Adrian McEwen

 */

#include <SPI.h>
#include <chibi.h>
//#include "TimerOne.h"
#define RX_BUFSIZE 300

#define NODE_ID 333

unsigned char buf[RX_BUFSIZE];
int len;
int dupe_cnt = 0;
unsigned char old[100];



/*
This struct will be common for all nodes
*/

#define CURRENT_TIME_REQUEST 0
#define CURRENT_TIME_RESPONSE 1
#define TECHRICE_PACKET 2

typedef struct{
  int8_t type;
  char payload[80];
} packet_t;

typedef struct{
  uint32_t year;
} datetime_t;


typedef struct{
  int32_t sensor_id;
  int32_t value;
} reading_t;


/*
This struct depends on the note type
*/
typedef struct{
  reading_t temperature;
  reading_t humidity;
  reading_t battery;
  reading_t solar;
  reading_t sonar;
  int32_t count;
  int32_t signal_strength;
  char timestamp[19];
  int32_t node_id;
} techrice_packet_t;






void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(57600);
  
  Serial.println("Init chibi stack");
  chibiInit();
  chibiSetShortAddr(NODE_ID);
  Serial.println("Init chibi stack complete");

  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.println("Started");
}



void loop()
{
  if (chibiDataRcvd() == true)
  { 
    
    int rssi, src_addr;
    len = chibiGetData(buf);
    if (len == 0) return;

    // retrieve the data and the signal strength
    rssi = chibiGetRSSI();
    src_addr = chibiGetSrcAddr();
    

    
    if (len)
    {
      packet_t request = *((packet_t*)(buf));
      print_packet_info(len, src_addr, rssi, request);


      if(request.type == CURRENT_TIME_REQUEST){
        
        // packet_t response;
        // response.type = CURRENT_TIME_RESPONSE;
        datetime_t now = {2016};
        // memcpy(response.payload, &now, sizeof(now));

        packet_t response = init_packet(CURRENT_TIME_RESPONSE, &now);
        chibiTx(src_addr, (uint8_t*)(&response), sizeof(response));
        Serial.println("Response sent");
      } else if (request.type == TECHRICE_PACKET){
        
        techrice_packet_t p = *((techrice_packet_t*)(request.payload));

        // Serial.print("data:");
        // Serial.println(packet.payload);
        p.signal_strength = rssi;
        p.node_id = NODE_ID;
        char http_body[300];

        sprintf(http_body, "format=compact&readings=%d,%d;%d,%d;%d,%d;%d,%d;%d,%d",
                  (int) p.temperature.sensor_id, (int) p.temperature.value,
                  (int) p.humidity.sensor_id, (int) p.humidity.value,
                  (int) p.battery.sensor_id, (int) p.battery.value,
                  (int) p.solar.sensor_id, (int) p.solar.value,
                  (int) p.sonar.sensor_id, (int) p.sonar.value);
        Serial.print("data: ");
        Serial.println(http_body);
      }
    }
  }

}

void print_packet_info(int len, int src_addr, int rssi, packet_t packet){
  Serial.println();
  Serial.print(millis());
  Serial.print(", Packet from: ");
  Serial.print(src_addr);
  Serial.print(", len: ");
  Serial.print(len);
  Serial.print(", signal strength: ");
  Serial.print(rssi);
  Serial.print(" , packet type: ");
  Serial.print(packet.type);
  Serial.print(", payload size: ");
  Serial.println(sizeof(packet.payload));  
}

packet_t init_packet(int type, void *payload){
  packet_t packet;
  packet.type = type;
  switch (type) {
      case CURRENT_TIME_REQUEST:
        break; // no payload to be copied
      case CURRENT_TIME_RESPONSE:
        memcpy(packet.payload, payload, sizeof(datetime_t));
        break;
      case TECHRICE_PACKET:
        memcpy(packet.payload, payload, sizeof(techrice_packet_t));
        break;
      default:
        break;
  }
  return packet;
}

