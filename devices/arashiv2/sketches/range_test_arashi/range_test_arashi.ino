#include <chibi.h>

#define RX_BUFSIZE 1000

#define NODE_ID 333

unsigned char buf[RX_BUFSIZE];

void setup() {
  Serial.begin(57600);

	Serial.println("Range Test Arashi v0.1");
  Serial.println("Init chibi stack");
  chibiInit();
  chibiSetShortAddr(NODE_ID);
  Serial.println("Init chibi stack complete");
}



void loop()
{
  if (chibiDataRcvd() == true)
  { 
    int rssi, src_addr, len;
    len = chibiGetData(buf);
    if (len == 0) return;
    
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


