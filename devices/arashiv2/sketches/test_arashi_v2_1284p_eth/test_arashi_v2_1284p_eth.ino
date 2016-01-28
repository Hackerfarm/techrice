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

char server[] = "iotree.org";    // name address for Google (using DNS)

// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192, 168, 1, 178);
//IPAddress ip(128, 199, 149, 82);

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(57600);
  
  Serial.println("Starting...");
  
//  Ethernet.begin(mac, ip);
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // no point in carrying on, so do nothing forevermore:
    // try to congifure using IP address instead of DHCP:
    Ethernet.begin(mac, ip);
  }
  chibiInit();
  chibiSetShortAddr(0x03);

  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.println("connecting...");

  // if you get a connection, report back via serial:
  if (client.connect(server, 80)) {
    Serial.println("connected");
    // Make a HTTP request:
    client.println("GET /nodes HTTP/1.1");
    client.println("Host: techrice.iotree.org");
    client.println("Connection: close");
    client.println();
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
       if (strcmp((char *)old, (char *)buf))
       {
         uint16_t tmp1, tmp2;
         
         tmp1 = chibiCmdStr2Num((char *)buf, 10);
         tmp2 = chibiCmdStr2Num((char *)old, 10);
         if ((tmp1 - tmp2) != 1)
         {
           Serial.print("Message received: "); Serial.print((char *)buf); Serial.print(" "); Serial.print(" ");Serial.print(rssi, DEC); Serial.print(" ");Serial.print(dupe_cnt); Serial.println("****** MISSING ******");
           dupe_cnt++;
         }
         else
         {
           Serial.print("Message received: "); Serial.print((char *)buf); Serial.print(" "); Serial.print(" ");Serial.print(rssi, DEC); Serial.print(" ");Serial.println(dupe_cnt);
         }
       }
       else
       {
         Serial.print("Message received: "); Serial.print((char *)buf); Serial.print(" "); Serial.print(rssi, HEX); Serial.print(" ");Serial.print(dupe_cnt); Serial.println("****** DUPE******");
         dupe_cnt++;
       }
       strcpy((char *)old, (char *)buf);
    }
  }
  
  
  // if there are incoming bytes available
  // from the server, read them and print them:
  if (client.available()) {
    char c = client.read();
    Serial.print(c);
  }

  // if the server's disconnected, stop the client:
  if (!client.connected()) {
    Serial.println();
    Serial.println("disconnecting.");
    client.stop();

    // do nothing forevermore:
    while (true);
  }
}

