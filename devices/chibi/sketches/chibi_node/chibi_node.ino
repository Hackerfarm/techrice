#include <chibi.h>
#include <Wire.h>
#include <SPI.h>
#include <stdint.h>



/*
START OF API-GENERATED HEADER
*/


#define TIME_PACKET 0
#define TECHRICE_PACKET 1

typedef struct{
  int8_t type;
  char payload[80];
} packet_t;


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

int hgmPin = 22;
int sdCsPin = 15;
int rtcCsPin = 28; 
int ledPin = 18;
int sdDetectPin = 19;
int vbatPin = 31;
int vsolPin = 29;
int sensorPin = 8;
int sonarTriggerPin = 5;
int sonarEchoPin = 7;
int sonarAwakePin = 10;
int burstModePin = 4;


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
}

/**************************************************************************/
// Loop
/**************************************************************************/
void loop()
{
  static int count = 0;
  
  // This function checks the command line to see if anything new was typed.
//  chibiCmdPoll();

  digitalWrite(sonarAwakePin, HIGH);

  /*if(r.sonar.value>10){
    digitalWrite(sonarAwakePin, LOW);
  }
  else{
    digitalWrite(sonarAwakePin, HIGH);
  }*/
  r.count++;
  // get_timestamp(r.timestamp);

  
  // packet_t packet = {TECHRICE_PACKET, (char*) &r};


  char sbuf[SBUF_SIZE];
  sprintf(sbuf, "Port: %d Bit: %d",digitalPinToPort(hgmPin), digitalPinToBitMask(hgmPin));
  Serial.println(sbuf);

//  r.timestamp = "2016-04-14 10:35:00";
  r.temperature.value = 28;
  r.humidity.value = 30;
  r.vbat.value = 4200;
  r.vsol.value = 6000;
  
  sprintf(sbuf, "Node_id: %d, cozunt: %d, timestamp: %19s, id %d: %dC (temperature), id %d: %d (humidity), id %d: %dmV (battery), id %d: %dmV (solar), id %d: %d cm (water level)", 
                (int) r.node_id,
                (int) r.count, 
                (int) r.timestamp,
                (int) r.temperature.sensor_id, (int) r.temperature.value,
                (int) r.humidity.sensor_id, (int) r.humidity.value,
                (int) r.vbat.sensor_id, (int) r.vbat.value,
                (int) r.vsol.sensor_id, (int) r.vsol.value,
                (int) r.distance_to_water_surface.sensor_id, (int) r.distance_to_water_surface.value);
  Serial.println(sbuf);

  packet_t packet;
  packet.type = TECHRICE_PACKET;
  memcpy(packet.payload, &r, sizeof(r));
   // = {TECHRICE_PACKET, (char*) &r};
  // packet_t packet = {TECHRICE_PACKET, "Hello"};
  Serial.print("payload size: ");
  Serial.println(sizeof(packet.payload));
  chibiTx(EDGE_ID, (unsigned char*)(&packet), sizeof(packet));
  free(sbuf);
  delay(5000);
}





