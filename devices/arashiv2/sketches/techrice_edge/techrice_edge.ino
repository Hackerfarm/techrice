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
#include <Ethernet.h>
#include <chibi.h>
//#include "TimerOne.h"
#define RX_BUFSIZE 300

#define NODE_ID 333

unsigned char buf[RX_BUFSIZE];
int len;
int dupe_cnt = 0;
unsigned char old[100];

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

char server[] = "api.techrice.jp";
const int port = 80;

// Set the static IP address to use if the DHCP fails to assign
//IPAddress ip(192, 168, 1, random(100,200));

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;


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






int lastConnection = millis();
void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(57600);

  // techrice_packet_t r = {
  //   {1,0},
  //   {1,0},
  //   {1,0},
  //   {1,0},
  //   {1,0},
  //   0,
  //   0,
  //   "",
  //   NODE_ID
  // };

  
  // packet_t p = {1, (char*)&r};
  Serial.println("Starting...");
  
//  Ethernet.begin(mac, ip);
  
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // no point in carrying on, so do nothing forevermore:
    for (;;)
      ;
  }
  // print your local IP address:
  printIPAddress();
  

  
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
  Ethernet.maintain();

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

      switch (request.type) {
          case CURRENT_TIME_REQUEST:{
              datetime_t now = {2016};
              packet_t response = init_packet(CURRENT_TIME_RESPONSE, &now);
              chibiTx(src_addr, (uint8_t*)(&response), sizeof(response));
              Serial.println("Response sent");
            }
            break;
          case TECHRICE_PACKET:{
              techrice_packet_t p = *((techrice_packet_t*)(request.payload));
              p.signal_strength = rssi;
              p.node_id = src_addr;
              char http_body[300];

              sprintf(http_body, "format=compact&readings=%d,%d;%d,%d;%d,%d;%d,%d;%d,%d",
                        (int) p.temperature.sensor_id, (int) p.temperature.value,
                        (int) p.humidity.sensor_id, (int) p.humidity.value,
                        (int) p.battery.sensor_id, (int) p.battery.value,
                        (int) p.solar.sensor_id, (int) p.solar.value,
                        (int) p.sonar.sensor_id, (int) p.sonar.value);
              Serial.print("data: ");
              Serial.println(http_body);
              api_post(http_body);
            }
            break;
          default:
            break;
      }
    }
  }

  client.stop();
}

void api_post(char *http_body){
  char http_header[400];
  sprintf(http_header, "POST /readings HTTP/1.1\r\nHost: api.techrice.jp\r\nAuthorization: Basic dGVjaHJpY2VAaGFja2VyLmZhcm06dW5peHRoZWdyZWF0\r\nContent-Length: %d\r\nUser-Agent: arashi2\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n", strlen(http_body));
  strcat(http_header, http_body);
  Serial.println("WHOLE REQUEST");
  Serial.println(http_header);
  client.stop();
  if (client.connect(server, port)) {
    Serial.println("connected");
    // Make a HTTP request:
    client.print(http_header);  
    client.flush();
    Serial.print("Done flushing");
    client.stop();
  }
  else {
    Serial.println("connection failed");
    client.stop();
  }
}

void printIPAddress()
{
  Serial.print("My IP address: ");
  for (byte thisByte = 0; thisByte < 4; thisByte++) {
    // print the value of each byte of the IP address:
    Serial.print(Ethernet.localIP()[thisByte], DEC);
    Serial.print(".");
  }

  Serial.println();
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




