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

unsigned char buf[100];
int len;
int dupe_cnt = 0;
unsigned char old[100];

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

char server[] = "iv-labs.org";
int32_t port = 4489;
char my_name[] = "saboten_sogoki";

// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192, 168, 1, 177);

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;


typedef struct{
  int32_t count;
  int32_t temperature;
  int32_t humidity;
  int32_t battery;
  int32_t solar;
  int32_t signal_strength;
} techrice_packet_t;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(57600);
  
  Serial.println("Starting...");
  
  Ethernet.begin(mac, ip);
  chibiInit();
  chibiSetShortAddr(0x03);

  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.println("connecting...");

  // if you get a connection, report back via serial:
  if (client.connect(server, port)) {
    Serial.println("connected");
    // Make a HTTP request:
    client.println("POST /post HTTP/1.0");
    client.println("Host: field-test.iv-labs.org");
    client.println("Content-Type: application/x-www-form-urlencoded; charset=utf-8");
    client.println("Content-Length: 44");
    client.println();
    client.println("identity=saboten_sogoki&content=switched_on");
    client.println();
    client.stop();
  }
  else {
    // kf you didn't get a connection to the server:
    Serial.println("connection failed");
  }
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
      techrice_packet_t packet = *((techrice_packet_t*)(buf));
      char sbuf[200];
      sprintf(sbuf, "Received following packet: \n\tCount: %d\n\tTemperature: %d\n\tHumidity: %d\n\tBattery (mV): %d\n\tSolar (mV): %d\n\tSignal: %d\n\n", 
                    (int)(packet.count),
                    (int)(packet.temperature), 
                    (int)(packet.humidity), 
                    (int)(packet.battery),
                    (int)(packet.solar),
                    (int)(packet.signal_strength));
      Serial.print(sbuf);
      
      if (client.connect(server, port)) {
      //if (true) {
        Serial.println("connected");
        // Make a HTTP request:
        client.println("POST /post HTTP/1.0");
        client.println("Host: field-test.iv-labs.org");
        client.println("Content-Type: application/x-www-form-urlencoded; charset=utf-8");
        client.println("Content-Length: 110");
        client.println();
        sprintf(sbuf, "identity=saboten_sogoki&content=%%7B%%22vbat%%22%%3A%d%%2C%%20%%22vsol%%22%%3A%d%%2C%%20%%22temperature%%22%%3A%d%%7D", (int)(packet.battery), (int)(packet.solar), (int)(packet.temperature));
        client.println(sbuf);
        Serial.println("Sent:");
        Serial.println(sbuf);
        client.println();
        client.println();
        client.println();
        client.println();
        client.println("\0");
        client.flush();
        client.stop();
      }
      else {
        Serial.println("connection failed");
        client.stop();
      }      
    }
  }
  
  
  // if there are incoming bytes available
  // from the server, read them and print them:
  /*while (client.available()) {
    char c = client.read();
    Serial.print(c);
  }*/
  client.stop();

  // if the server's disconnected, stop the client:
  /*if (!client.connected()) {
    //Serial.println();
    //Serial.println("disconnecting.");
    client.stop();

    // do nothing forevermore:
    //while (true);
  }*/
}

