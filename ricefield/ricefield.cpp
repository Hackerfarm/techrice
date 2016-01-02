// rm -r * && cmake .. && make && make upload && screen -S saboten /dev/tty.usbserial-A501K9HW 57600,sc8
// #include <string>
#include "ricefield.h"
#include <saboten.h>
#include <chibi.h>
// #include <satoyama_config.h>
// #include <SPI.h>
// #include <SD.h>

#include <SPI.h>



Saboten *board = new Saboten(1, 57600);


void setup()
{
  board->register_sensor(new Paralax28015REVC_Sensor(1, 5));  
  chibiCmdInit(57600);
  board->init_sdcard();
  
  // This should be done using NTP
  board->set_datetime(16, 1, 2, 14, 20, 0);
  char msg[100];
  memset(msg, 0, 100);
  sprintf(msg, "Clock set to: %s", (char*)board->timestamp());
  board->writeData((unsigned char*)msg);
  free(msg);
  

}

void loop()
{ 
  uint8_t tx_buf[TX_LENGTH];
  memset(tx_buf, 0, TX_LENGTH);
  // std::string buffer;
  board->read_sensors(tx_buf);
  board->read_board_diagnostics(tx_buf);
  
  Serial.print("Data in buffer: ");
  Serial.println((char*) tx_buf);
  
  // chibiTx(AGGREGATOR_SHORT_ADDRESS, tx_buf, TX_LENGTH);
  board->writeData(tx_buf);
  
  free(tx_buf);
  delay(1000);
  
  
  for(int i = 0; i < 60; i++){
    board->sleep_mcu();
  }
}

