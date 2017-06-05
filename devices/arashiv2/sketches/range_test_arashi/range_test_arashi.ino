#include <SPI.h>
#include <Ethernet.h>
#include <chibi.h>

#define RX_BUFSIZE 1000

#define NODE_ID 333

int ledPin = 4;

unsigned char buf[RX_BUFSIZE];

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);

void setup() {
  Serial.begin(57600);
  // ethernet chip select pin
  // do not remove or the radio won't initialize correctly
  pinMode(31, OUTPUT);
  digitalWrite(31, HIGH);

  Serial.println("Range Test Arashi v0.1");
  Serial.println("Init chibi stack");


  chibiInit();
  chibiSetShortAddr(NODE_ID);
  Serial.println("Init chibi stack complete");
  pinMode(ledPin, OUTPUT);
  Ethernet.begin(mac, ip);

}



void loop()
{
  if (chibiDataRcvd() == true)
  { 
    digitalWrite(ledPin, HIGH);
    int rssi, src_addr, len;
    len = chibiGetData(buf);
    if (len == 0) {
      Serial.println("Null packet received");
      return;
    }
    
    // retrieve the data and the signal strength
    rssi = chibiGetRSSI();
    src_addr = chibiGetSrcAddr();
    Serial.print("Signal strength: ");
    Serial.print(rssi);
		Serial.print("\t");
    if (len)
    {
			Serial.println((char*)(buf));
    }
  }
}


