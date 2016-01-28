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

#define NODE_ID 3

unsigned char buf[RX_BUFSIZE];
int len;
int dupe_cnt = 0;
unsigned char old[100];

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

char server[] = "iotree.org";    // name address for Google (using DNS)
//char httpHeader[] = "GET /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nConnection: close\r\nAccept: */*\r\nUser-Agent: python-requests/2.9.1\r\n\r\n";
char httpHeader[] = "POST /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nContent-Length: 33\r\nAuthorization: Basic dGVjaHJpY2VAaGFja2VyLmZhcm06dW5peHRoZWdyZWF0\r\nAccept: */*\r\nUser-Agent: arashi2\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nreadings=1%2C23.5%2C1453202011.48";

//char httpHeader[500];
//sprintf(httpHeader, "ej%d", 5);
//String httpHeader = "GET /posttest HTTP/1.1\r\n" +"Host: techrice.iotree.org\r\nContent-Length: 33\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: python-requests/2.9.1\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nreadings=1%2C23.5%2C1453202011.48";

// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192, 168, 1, random(100,200));

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;


/*
This struct will be common for all nodes
*/
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
  int32_t count;
  int32_t signal_strength;
  char timestamp[19];
  int32_t node_id;
} techrice_packet_t;





int lastConnection = millis();
void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(57600);
  
  Serial.println("Starting...");
  
//  Ethernet.begin(mac, ip);
  
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // no point in carrying on, so do nothing forevermore:
    // try to congifure using IP address instead of DHCP:
//    Ethernet.begin(mac, ip);
  }
  
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
    if (len)
    {
      Serial.println("1");
      techrice_packet_t p = *((techrice_packet_t*)(buf));
      Serial.println("2");
      p.signal_strength = rssi;
      Serial.println("3");
      char http_body[300];
      Serial.println("4");
      sprintf(http_body, "format=compact&readings=%d,%d;%d,%d;%d,%d;%d,%d&timestamp=%s&node_id=%s,rssi=%d",
                (int) p.temperature.sensor_id, (int) p.temperature.value,
                (int) p.humidity.sensor_id, (int) p.humidity.value,
                (int) p.battery.sensor_id, (int) p.battery.value,
                (int) p.solar.sensor_id, (int) p.solar.value,
                p.timestamp,
                p.node_id,
                p.signal_strength);
      Serial.println("5");
      api_post(http_body);
      Serial.println("10");
    }
  }
  
  
  if (client.available()) {
    char c = client.read();
    Serial.print(c);
  }


}

void api_post(char *http_body){
  
  char http_header[400];
  sprintf(http_header, "POST /readings HTTP/1.1\r\nHost: techrice.iotree.org\r\nAuthorization: Basic dGVjaHJpY2VAaGFja2VyLmZhcm06dW5peHRoZWdyZWF0\r\nContent-Length: %d\r\nAccept: */*\r\nUser-Agent: arashi2\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n", strlen(http_body));
  strcat(http_header, http_body);
  Serial.println("WHOLE REQUEST");
  Serial.println(http_header);
  client.stop();
  if (client.connect(server, 80)) {
    client.print(http_header);
  }
  else {
    // kf you didn't get a connection to the server:
    Serial.println("connection failed");
  }

}




void simple_post(){
  client.stop();
//  while(!client.connect(server, 80)){
//    Serial.println("")
//  }
  if (client.connect(server, 80)) {
    Serial.println("connected");
    // Make a HTTP request:
    client.print(httpHeader);
//    client.println("GET /nodes HTTP/1.1");
//    client.println("Host: techrice.iotree.org");
//    client.println("Connection: close");
//    client.println();
  }
  else {
    // kf you didn't get a connection to the server:
    Serial.println("connection failed");
  }
}

void adv_post(){
  char http_body[] = "readings";
  char data[] = "1,23.5,1453202011.48";
  char http_header[200];
  sprintf(http_header, "POST /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nContent-Length: %d\r\nAccept: */*\r\nUser-Agent: arashi2\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n", strlen(http_body));
  strcat(http_header, http_body);
  client.stop();

//  Serial.println("Stopped client.");
//  while(!client.connect(server, 80)){
//    Serial.println("")
//  }
  if (client.connect(server, 80)) {
    Serial.println("connected");
    // Make a HTTP request:
    
    client.print(httpHeader);
    client.print(data);
  }
  else {
    // kf you didn't get a connection to the server:
    Serial.println("connection failed");
  }

}

