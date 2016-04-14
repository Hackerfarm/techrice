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

#define TIME_PACKET 0
#define TECHRICE_PACKET 1

// typedef struct{
//   int8_t type;
//   char *payload;
// } packet_t;

typedef struct{
  int8_t type;
  char payload[80];
} packet_t;


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
    Serial.println(len);
    Serial.print("Signal strength: ");
    Serial.println(rssi);
    if (len)
    {
      
      packet_t packet = *((packet_t*)(buf));
      Serial.print("Packet type: ");
      Serial.println(packet.type);
      techrice_packet_t p = *((techrice_packet_t*)(packet.payload));
      Serial.print("payload size: ");
      Serial.println(sizeof(packet.payload));
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
