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

unsigned char buf[RX_BUFSIZE];
int len;
int dupe_cnt = 0;
unsigned char old[100];

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

char server[] = "iotree.org";    // name address for Google (using DNS)
//char httpHeader[] = "GET /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nConnection: close\r\nAccept: */*\r\nUser-Agent: python-requests/2.9.1\r\n\r\n";
char httpHeader[] = "POST /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nContent-Length: 33\r\nAccept: */*\r\nUser-Agent: arashi2\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nreadings=1%2C23.5%2C1453202011.48";

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
  chibiSetShortAddr(0x03);
  Serial.println("Init chibi stack complete");

  // give the Ethernet shield a second to initialize:
  delay(1000);
//  Serial.println("connecting...");
//
  adv_post();
  delay(2000);
  Serial.println("Started");
}



void loop()
{
  
  int mil = millis();
  
//  if((mil % 10000 > 0) & (mil % 10000 < 10)){
//    Serial.println("TICK");
//    simple_post();
//  }
  
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
      techrice_packet_t p = *((techrice_packet_t*)(buf));
//      Serial.println((char*)buf);
//      char sbuf[200];
//      sprintf(sbuf, "Count: %d, timestamp: %s, id %d: %dC (temperature), id %d: %d (humidity), id %d: %dmV (battery), id %d: %dmV (solar),", 
//                (int) p.count, 
//                (int) p.timestamp,
//                (int) p.temperature.sensor_id, (int) p.temperature.value,
//                (int) p.humidity.sensor_id, (int) p.humidity.value,
//                (int) p.battery.sensor_id, (int) p.battery.value,
//                (int) p.solar.sensor_id, (int) p.solar.value);
//      Serial.println(sbuf);
//      free(sbuf);
      char http_body[200];
      sprintf(http_body, "readings=%d,%d;%d,%d;%d,%d;%d,%d;",
                (int) p.temperature.sensor_id, (int) p.temperature.value,
                (int) p.humidity.sensor_id, (int) p.humidity.value,
                (int) p.battery.sensor_id, (int) p.battery.value,
                (int) p.solar.sensor_id, (int) p.solar.value);
      api_post(http_body);
      Serial.println("HTTP_BODY");
      Serial.println(http_body);
      Serial.println(strlen(http_body));
//      char request[1000];
//      sprintf(request, "POST /newtest HTTP/1.1\n\tHost: techrice.iotree.org\n\tUser-Agent: arduino-ethernet-home\n\tContent-Type: application/x-www-form-urlencoded\n\tConnection: close\n\tContent-length: %d\n\tformat=compact&data=1", 21);  
//      sprintf(request, "GET /newtest HTTP/1.1\n\tHost: techrice.iotree.org\n\tAccept: */*\r\n\tConnection: close\n\t");  
//      if (client.connect(server, 80)) {
//        Serial.println("Sending request:");
//        Serial.println(request);
////        client.print(request); 
//      } 
//      else {
//        // if you couldn't make a connection:
//        Serial.println("connection failed, disconnecting");
//        client.stop();
//      } 
    }
  }
  
  
  
//  
  // if there are incoming bytes available
  // from the server, read them and print them:
  if (client.available()) {
    char c = client.read();
    Serial.print(c);
  }


}

void api_post(char *http_body){
  
//  char http_body[] = "readings=";
//  char data[] = "1,23.5,1453202011.48";
//  char request[500];
//  Serial.print("LENGTH: ");
//  int i = strlen((char*) buf);
//  Serial.println(i);
  Serial.println("IN FUNCTION");
  Serial.println(http_body);
  Serial.println(strlen(http_body));
  char http_header[300];
  sprintf(http_header, "POST /posttest HTTP/1.1\r\nHost: techrice.iotree.org\r\nContent-Length: %d\r\nAccept: */*\r\nUser-Agent: arashi2\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n", strlen(http_body));
  strcat(http_header, http_body);
//  Serial.println(http_header);
//  strcat(http_header, http_body);
  Serial.println("WHOLE REQUEST");
  Serial.println(http_header);
  client.stop();
  if (client.connect(server, 80)) {
    Serial.println("connected");
    // Make a HTTP request:
    
    client.print(http_header);
//    client.print(buf);
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

