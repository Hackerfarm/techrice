#include <chibi.h>
#include <Wire.h>
#include <SPI.h>
#include <stdint.h>
#include <avr/time.h>


/*
START OF API-GENERATED HEADER
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




typedef struct{
  reading_t vsol;
  reading_t vbat;
  reading_t temperature;
  reading_t humidity;
  reading_t distance_to_water_surface;
  int32_t count;
  int32_t signal_strength;
  char timestamp[19];
  int32_t node_id;
} techrice_packet_t;

#define NODE_ID 2
#define EDGE_ID BROADCAST_ADDR
#define VSOL_SENSOR_ID 6
#define VBAT_SENSOR_ID 7
#define TEMPERATURE_SENSOR_ID 8
#define HUMIDITY_SENSOR_ID 9
#define DISTANCE_TO_WATER_SURFACE_SENSOR_ID 10


techrice_packet_t r = {
  {VSOL_SENSOR_ID,0},
  {VBAT_SENSOR_ID,0},
  {TEMPERATURE_SENSOR_ID,0},
  {HUMIDITY_SENSOR_ID,0},
  {DISTANCE_TO_WATER_SURFACE_SENSOR_ID,0},
  0,
  0,
  "",
  NODE_ID
};



/*
END OF OF API-GENERATED HEADER
*/





#define SBUF_SIZE 200 //Note that due to inefficient implementation of sd_write() the memory footprint is actually twice of this value. 

#define DATECODE "08-09-2014"
#define ADCREFVOLTAGE 3.3



// Pins that will not interfer with the SPI: 2 to 5, 7 to 10 + 14 and 15

int dupe_cnt = 0;
unsigned char old[100];

unsigned char buf[100];

// this is for printf


void setup()
{    
  // Initialize the chibi command line and set the speed to 57600 bps
  chibiCmdInit(57600);
  // Initialize the chibi wireless stack
  chibiInit();
  request_time();
  

}

/**************************************************************************/
// Loop
/**************************************************************************/
void loop()
{
  static int count = 0;
  
  r.count++;
  char sbuf[SBUF_SIZE];

//  r.timestamp = "2016-04-14 10:35:00";
  r.temperature.value = 28;
  r.humidity.value = 30;
  r.vbat.value = 4200;
  r.vsol.value = 6000;
  
  sprintf(sbuf, "Node_id: %d, count: %d, timestamp: %19s, id %d: %dC (temperature), id %d: %d (humidity), id %d: %dmV (battery), id %d: %dmV (solar), id %d: %d cm (water level)", 
                (int) r.node_id,
                (int) r.count, 
                (int) r.timestamp,
                (int) r.temperature.sensor_id, (int) r.temperature.value,
                (int) r.humidity.sensor_id, (int) r.humidity.value,
                (int) r.vbat.sensor_id, (int) r.vbat.value,
                (int) r.vsol.sensor_id, (int) r.vsol.value,
                (int) r.distance_to_water_surface.sensor_id, (int) r.distance_to_water_surface.value);
  Serial.println(sbuf);

  // packet_t request;
  // request.type = TECHRICE_PACKET;
  // memcpy(request.payload, &r, sizeof(r));

  packet_t request = init_packet(TECHRICE_PACKET, &r);

   // = {TECHRICE_PACKET, (char*) &r};
  // packet_t request = {TECHRICE_PACKET, "Hello"};
  Serial.print("payload size: ");
  Serial.println(sizeof(request.payload));
  chibiTx(EDGE_ID, (unsigned char*)(&request), sizeof(request));
  free(sbuf);
  delay(5000);
}



int request_time(){
  Serial.println("Sending request for current time");
  packet_t request = init_packet(CURRENT_TIME_REQUEST, (void *)0);
  chibiTx(EDGE_ID, (uint8_t*)(&request), sizeof(request));
  free(&request);

  while(!chibiDataRcvd()); // Wait forever until response
  
  int rssi, src_addr;
  int len = chibiGetData(buf);
  if (len == 0) return 0;

  // retrieve the data and the signal strength
  rssi = chibiGetRSSI();
  src_addr = chibiGetSrcAddr();
  
  packet_t response = *((packet_t*)(buf));
  print_packet_info(len, src_addr, rssi, response);
  // datetime_t now = *((datetime_t*)(response.payload));
  if(len){
    if(response.type == CURRENT_TIME_RESPONSE){
       datetime_t now = *((datetime_t*)(response.payload));
        Serial.print("time now: ");
        Serial.println(now.year);
    }
    // switch (response.type) {
    //   case CURRENT_TIME_RESPONSE:
    //     // do something
    //     datetime_t now = *((datetime_t*)(response.payload));
    //     Serial.print("time now: ");
    //     Serial.println(now.year);
    //     break;
    //   default:
    //     Serial.print("Expected CURRENT_TIME_RESPONSE, but got ");        
    //     Serial.println(response.type);
    //     break;
    //     // do something
    // }
  }
  delay(2000);
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

