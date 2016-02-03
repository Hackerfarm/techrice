#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>
#include <chibi.h>
#include <Wire.h>
#include <SPI.h>
#include <SdFat.h>
#include <pcf2127.h>
#include <stdint.h>

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

/*
These values will be provided by the API
*/
#define NODE_ID 1
#define EDGE_ID 3
#define TEMPERATURE_SENSOR_ID 3
#define HUMIDITY_SENSOR_ID 4
#define BATTERY_SENSOR_ID 2
#define SOLAR_SENSOR_ID 1
#define SONAR_SENSOR_ID 5

techrice_packet_t r = {
  {TEMPERATURE_SENSOR_ID,0}, 
  {HUMIDITY_SENSOR_ID,0},
  {BATTERY_SENSOR_ID,0}, 
  {SOLAR_SENSOR_ID,0},
  0,
  0,
  "",
  NODE_ID
};


SdFat sd;
SdFile myFile;

#define DATECODE "08-09-2014"
#define TITLE "SABOTEN 900 MHz Long Range\n"
#define FILENAME "TECHRICE.TXT"
#define ADCREFVOLTAGE 3.3

int hgmPin = 14;
int sdCsPin = 15;
int rtcCsPin = 28; 
int ledPin = 18;
int sdDetectPin = 19;
int vbatPin = 31;
int vsolPin = 29;

int dupe_cnt = 0;
unsigned char old[100];

unsigned char buf[100];

// this is for printf
static FILE uartout = {0};  

PCF2127 pcf(0, 0, 0, rtcCsPin);











void setup()
{    
  uint8_t i, sdDetect;
  // fill in the UART file descriptor with pointer to writer.
  fdev_setup_stream (&uartout, uart_putchar, NULL, _FDEV_SETUP_WRITE);
  
  // The uart is the standard output device STDOUT.
  stdout = &uartout ;
  
  old[0] = 3;
  
  // set up high gain mode pin
  pinMode(hgmPin, OUTPUT);
  digitalWrite(hgmPin, LOW);
  
  // set up rtc chip select
  pinMode(rtcCsPin, OUTPUT);
  digitalWrite(rtcCsPin, HIGH);
  
  pinMode(sdCsPin, OUTPUT);
  digitalWrite(sdCsPin, HIGH);
  
  // set up sd card detect
  pinMode(sdDetectPin, INPUT);
  digitalWrite(sdDetectPin, HIGH);
  
  // set up battery monitoring
  pinMode(vbatPin, INPUT);
  
  // set up LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  //delay(300);
  //digitalWrite(ledPin, LOW);
  
  // Initialize the chibi command line and set the speed to 57600 bps
  chibiCmdInit(57600);
  

  pcf.enableMinuteInterrupt();
//  pcf.enableSecondInterrupt();
  pcf.setInterruptToPulse();
  attachInterrupt(2, rtcInterrupt, FALLING);
  
  // Initialize the chibi wireless stack
  chibiInit();
  
  // set up chibi regs for external P/A
  //chibiRegWrite(0x4, 0xA0);
    
  // datecode version
  printf(TITLE);
  printf("Datecode: %s\n", DATECODE);

  pcf.writeDate(16, 1, 24, 6);
  pcf.writeTime(13, 8, 0);

  chibiSetShortAddr(NODE_ID);

  Serial.print("NODE_ID: ");
  Serial.println(r.node_id);
  /*
  // check for SD and init
  sdDetect = digitalRead(sdDetectPin);
  if (sdDetect == 0)
  {
    // init the SD card
    if (!sd.begin(sdCsPin)) 
    {
      
      Serial.println("Card failed, or not present");
      sd.initErrorHalt();
      return;
    }
    printf("SD Card is initialized.\n");
  }
  else
  {
    printf("No SD card detected.\n");
  }
  */

  // This is where you declare the commands for the command line.
  // The first argument is the alias you type in the command line. The second
  // argument is the name of the function that the command will jump to.
  
  chibiCmdAdd("getsaddr", cmdGetShortAddr);  // set the short address of the node
  chibiCmdAdd("setsaddr", cmdSetShortAddr);  // get the short address of the node
  chibiCmdAdd("send", cmdSend);   // send the string typed into the command line
  chibiCmdAdd("send2", cmd_tx2);  
  chibiCmdAdd("rd", cmd_reg_read);   // send the string typed into the command line
  chibiCmdAdd("wr", cmd_reg_write);   // send the string typed into the command line
  chibiCmdAdd("slr", cmdSleepRadio);
  chibiCmdAdd("slm", cmdSleepMcu);
  chibiCmdAdd("sdw", cmdSdWrite);
  chibiCmdAdd("time", cmdWriteTime);
  chibiCmdAdd("date", cmdWriteDate);
  chibiCmdAdd("rdt", cmdReadDateTime);
  chibiCmdAdd("bat", cmdVbatRead);
  chibiCmdAdd("sol", cmdVsolRead);
  
  chibiCmdAdd("tmp", cmdReadTemp);
  
  // high gain mode
  digitalWrite(hgmPin, HIGH);

  
}

/**************************************************************************/
// Loop
/**************************************************************************/
void loop()
{
  static int count = 0;
  
  // This function checks the command line to see if anything new was typed.
//  chibiCmdPoll();

  get_temp(r.temperature.value, r.humidity.value);
  get_vbat(r.battery.value);
  get_vsol(r.solar.value);
  r.count++;
  get_timestamp(r.timestamp);

  char sbuf[200];
  sprintf(sbuf, "Node_id: %d, count: %d, timestamp: %19s, id %d: %dC (temperature), id %d: %d (humidity), id %d: %dmV (battery), id %d: %dmV (solar),", 
                (int) r.node_id,
                (int) r.count, 
                (int) r.timestamp,
                (int) r.temperature.sensor_id, (int) r.temperature.value,
                (int) r.humidity.sensor_id, (int) r.humidity.value,
                (int) r.battery.sensor_id, (int) r.battery.value,
                (int) r.solar.sensor_id, (int) r.solar.value);
  Serial.println(sbuf);
//  char hum[19];
//  get_timestamp(hum);
  chibiTx(EDGE_ID, (unsigned char*)(&r), sizeof(r));
//  delay(10000);
//  for(int i=0; i<10; i++){
//    digitalWrite(ledPin, HIGH);
//    delay(500);
//    digitalWrite(ledPin, LOW);
//    delay(500);  
//    }
  
  sleep_mcu();

  
  // Check if any data was received from the radio. If so, then handle it.
 /* if (chibiDataRcvd() == true)
  { 
    int len, rssi, src_addr;
    byte buf[100];  // this is where we store the received data
    
    // retrieve the data and the signal strength
    len = chibiGetData(buf);
    
    if (len == 0) break;
    
    rssi = chibiGetRSSI();
    src_addr = chibiGetSrcAddr();
  
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
  }*/
}

void rtcInterrupt(){
  Serial.println("Interrupt");
  detachInterrupt(2);
// for(int i=0; i<10; i++){
//    digitalWrite(ledPin, HIGH);
//    delay(200);
//    digitalWrite(ledPin, LOW);
//    delay(200);  
//    }
}

void sleep_radio(){
  digitalWrite(hgmPin, LOW);
  // set up chibi regs to turn off external P/A
  chibiRegWrite(0x4, 0x20);
  chibiSleepRadio(1);  
}

void wakeup_radio(){
  chibiSleepRadio(0);
  digitalWrite(hgmPin, HIGH);
  // set up chibi regs to turn on external P/A
  chibiRegWrite(0x4, 0xA0);
  
  
}

void sleep_mcu(){
  attachInterrupt(2, rtcInterrupt, FALLING);
  delay(100);

  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_radio();
  sleep_enable();        // setting up for sleep ...
  
  ADCSRA &= ~(1 << ADEN);    // Disable ADC
  Serial.println("Going to sleep");
  delay(100);
  digitalWrite(ledPin, LOW);
  sleep_mode();

  sleep_disable();
  Serial.println("Awake");
  digitalWrite(ledPin, HIGH);
  wakeup_radio();
  ADCSRA |= (1 << ADEN); // Enable ADC
}



void get_timestamp(char tbuf[19])
{
  uint8_t hours, minutes, seconds;
  uint8_t year, month, day, weekday;
  
  pcf.readTime(&hours, &minutes, &seconds);
  pcf.readDate(&year, &month, &day, &weekday);

//  char tbuf[19];
  sprintf(tbuf, "%u-%u-%u %u:%u:%u", year, month, day, hours, minutes, seconds);
  Serial.println(tbuf);
//  Serial.println("Year: %d, Month: %d, Day: %d, Weekday: %d Hours: %d, Minutes: %d, Seconds: %d\n", year, month, day, weekday, hours, minutes, seconds);
}

void init_datetime(int arg_cnt, char **args)
{
  uint8_t year, month, day, weekday;
  
  year = chibiCmdStr2Num(args[1], 10);
  month = chibiCmdStr2Num(args[2], 10);
  day = chibiCmdStr2Num(args[3], 10);
  weekday = chibiCmdStr2Num(args[4], 10);
  pcf.writeDate(2016, 1, 24, 6);
  
  pcf.readDate(&year, &month, &day, &weekday);
  printf("Year: %d, Month: %d, Day: %d, Weekday: %d\n", year, month, day, weekday);
}



/**************************************************************************/
// USER FUNCTIONS
/**************************************************************************/

/**************************************************************************/
/*!
    Get short address of device from EEPROM
    Usage: getsaddr
*/
/**************************************************************************/
void cmdGetShortAddr(int arg_cnt, char **args)
{
  int val;
  
  val = chibiGetShortAddr();
  Serial.print("Short Address: "); Serial.println(val, HEX);
}

/**************************************************************************/
/*!
    Write short address of device to EEPROM
    Usage: setsaddr <addr>
*/
/**************************************************************************/
void cmdSetShortAddr(int arg_cnt, char **args)
{
  int val;
  
  val = chibiCmdStr2Num(args[1], 16);
  chibiSetShortAddr(val);
}

/**************************************************************************/
/*!
    Transmit data to another node wirelessly using Chibi stack. Currently
    only handles ASCII string payload
    Usage: send <addr> <string...>
*/
/**************************************************************************/
void cmdSend(int arg_cnt, char **args)
{
    byte data[100];
    int addr, len;

    // convert cmd line string to integer with specified base
    addr = chibiCmdStr2Num(args[1], 16);
    
    // concatenate strings typed into the command line and send it to
    // the specified address
    len = strCat((char *)data, 2, arg_cnt, args);    
    chibiTx(addr, data,len);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
// Gives a mV result
bool get_vbat(int32_t &battery)
{
  unsigned int vbat = analogRead(vbatPin);
  battery = (int32_t)(((vbat/1023.0) * ADCREFVOLTAGE) * 2000);
  return true;
}

void cmdVbatRead(int arg_cnt, char **args)
{
  int32_t b;
  get_vbat(b);
  Serial.print("Battery voltage: "); Serial.println((float)(b/1000.0), 1);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
// gives a mV result
bool get_vsol(int32_t &solar)
{
  unsigned int vsol = analogRead(vsolPin);
  solar = (int32_t)(((vsol/1023.0) * ADCREFVOLTAGE) * 2000);
}

void cmdVsolRead(int arg_cnt, char **args)
{
  int32_t s;
  get_vsol(s);
  Serial.print("Solar voltage: "); Serial.println((float)(s/1000.0), 1);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmdSdWrite(int arg_cnt, char **args)
{
    char data[100];
    
    // concatenate strings typed into the command line and send it to
    // the specified address
    strCat(data, 1, arg_cnt, args);  
    
    if (!myFile.open(FILENAME, O_RDWR | O_CREAT | O_AT_END))

    {
      myFile.println(data);
      myFile.close();
    }
    else
    {
      printf("Error opening dataFile\n");
    }
}

/**************************************************************************/
/*!
    Read radio registers via SPI.
    Usage: rd <addr>
*/
/**************************************************************************/
void cmd_reg_read(int arg_cnt, char **args)
{
    uint8_t addr, val;

    addr = strtol(args[1], NULL, 16);
    val = chibiRegRead(addr);

    sprintf((char *)buf, "Reg Read: %04X, %02X.\n", addr, val);
    Serial.print((char *)buf);
}

/**************************************************************************/
/*!
    Write radio registers via SPI
    Usage: wr <addr> <val>
*/
/**************************************************************************/
void cmd_reg_write(int arg_cnt, char **args)
{
    uint8_t addr, val;

    addr = strtol(args[1], NULL, 16);
    val = strtol(args[2], NULL, 16);

    chibiRegWrite(addr, val);
    sprintf((char *)buf, "Write: %04X, %02X.\n", addr, val);
    Serial.print((char *)buf);

    val = chibiRegRead(addr);
    sprintf((char *)buf, "Readback: %04X, %02X.\n", addr, val);
    Serial.print((char *)buf);
}


/**************************************************************************/
// 
/**************************************************************************/
void cmdSleepMcu(int arg_cnt, char **args)
{
  printf("Sleeping MCU\n");
  delay(100);
  
  // set pullups on inputs
//  pinMode(sdCsPin, INPUT);
//nn  digitalWrite(sdCsPin, HIGH);
  
//  pinMode(sdDetectPin, INPUT);
  digitalWrite(sdDetectPin, LOW);

  digitalWrite(ledPin, LOW);
  
  attachInterrupt(2, rtcInterrupt, FALLING);
  delay(100);

  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  chibiSleepRadio(0);
  sleep_enable();        // setting up for sleep ...
  
  ADCSRA &= ~(1 << ADEN);    // Disable ADC
  sleep_mode();

  sleep_disable();
  ADCSRA |= (1 << ADEN);
  digitalWrite(ledPin, HIGH);
  chibiSleepRadio(1);
}

/**************************************************************************/
// 
/**************************************************************************/
void cmdSleepRadio(int arg_cnt, char **args)
{
  int val = strtol(args[1], NULL, 10);
  
  if (val)
  {
    digitalWrite(hgmPin, LOW);
  
    // set up chibi regs to turn off external P/A
    chibiRegWrite(0x4, 0x20);
  }
  else
  {
    digitalWrite(hgmPin, HIGH);
    
    // set up chibi regs to turn on external P/A
    chibiRegWrite(0x4, 0xA0);
  }
  
  // turn on/off radio
  chibiSleepRadio(val);
}

/**************************************************************************/
// 
/**************************************************************************/


void cmdReadDateTime(int arg_cnt, char **args)
{
  uint8_t hours, minutes, seconds;
  uint8_t year, month, day, weekday;
  
  pcf.readTime(&hours, &minutes, &seconds);
  pcf.readDate(&year, &month, &day, &weekday);
  
  printf("Year: %d, Month: %d, Day: %d, Weekday: %d Hours: %d, Minutes: %d, Seconds: %d\n", year, month, day, weekday, hours, minutes, seconds);
}

/**************************************************************************/
// 
/**************************************************************************/
void cmdWriteTime(int arg_cnt, char **args)
{
  uint8_t hours, minutes, seconds;
  
  hours = chibiCmdStr2Num(args[1], 10);
  minutes = chibiCmdStr2Num(args[2], 10);
  seconds = chibiCmdStr2Num(args[3], 10);
  pcf.writeTime(hours, minutes, seconds);
  
  pcf.readTime(&hours, &minutes, &seconds);
  printf("Hours: %d, Minutes: %d, Seconds: %d\n", hours, minutes, seconds);
}

/**************************************************************************/
// 
/**************************************************************************/
void cmdWriteDate(int arg_cnt, char **args)
{
  uint8_t year, month, day, weekday;
  
  year = chibiCmdStr2Num(args[1], 10);
  month = chibiCmdStr2Num(args[2], 10);
  day = chibiCmdStr2Num(args[3], 10);
  weekday = chibiCmdStr2Num(args[4], 10);
  pcf.writeDate(year, month, day, weekday);
  
  pcf.readDate(&year, &month, &day, &weekday);
  printf("Year: %d, Month: %d, Day: %d, Weekday: %d\n", year, month, day, weekday);
}



bool get_temp(int32_t &temperature, int32_t& humidity){
    
    // It's ugly, isn't it?
    int pin = 8;
    int ret = 0;
    uint8_t bits[5];
    const int DHTLIB_TIMEOUT = (F_CPU/40000);
  
    // INIT BUFFERVAR TO RECEIVE DATA
    uint8_t mask = 128;
    uint8_t idx = 0;

    uint8_t bit = digitalPinToBitMask(pin);
    uint8_t port = digitalPinToPort(pin);
    volatile uint8_t *PIR = portInputRegister(port);

    // EMPTY BUFFER
    for (uint8_t i = 0; i < 5; i++) bits[i] = 0;

    // REQUEST SAMPLE
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW); // T-be 
    delay(18);  //delay(wakeupDelay);
    digitalWrite(pin, HIGH);   // T-go
    delayMicroseconds(40);
    pinMode(pin, INPUT);

    // GET ACKNOWLEDGE or TIMEOUT
    uint16_t loopCntLOW = DHTLIB_TIMEOUT;
    while ((*PIR & bit) == LOW )  // T-rel
    {
        if (--loopCntLOW == 0) return false;
    }

    uint16_t loopCntHIGH = DHTLIB_TIMEOUT;
    while ((*PIR & bit) != LOW )  // T-reh
    {
        if (--loopCntHIGH == 0) return false;
    }

    // READ THE OUTPUT - 40 BITS => 5 BYTES
    for (uint8_t i = 40; i != 0; i--)
    {
        loopCntLOW = DHTLIB_TIMEOUT;
        while ((*PIR & bit) == LOW )
        {
            if (--loopCntLOW == 0) return false;
        }

        uint32_t t = micros();

        loopCntHIGH = DHTLIB_TIMEOUT;
        while ((*PIR & bit) != LOW )
        {
            if (--loopCntHIGH == 0) return false;
        }

        if ((micros() - t) > 40)
        { 
            bits[idx] |= mask;
        }
        mask >>= 1;
        if (mask == 0)   // next byte?
        {
            mask = 128;
            idx++;
        }
    }
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
    humidity = bits[0];
    temperature = bits[2];
    return true;
}



/**************************************************************************/
/*!
    Reads temperature and humidity from the sensor and displays it
    Usage: tmp
*/
/**************************************************************************/
void cmdReadTemp(int arg_cnt, char **args)
{
  int32_t t, h;
  get_temp(t, h);

    Serial.print("Humidity: ");
    Serial.println(h);
    Serial.print("Temperature: ");
    Serial.println(t);
}

/**************************************************************************/
/*!
    Transmit data to another node wirelessly using Chibi stack.
    Usage: send <addr> <string...>
*/
/**************************************************************************/
void cmd_tx2(int arg_cnt, char **args)
{
    unsigned char data[6];
    int i, addr, len;

    addr = chibiCmdStr2Num(args[1], 16);
    
    for (i=0; i<1000; i++)
    {
      sprintf((char *)data, "%04d", i);
      data[4] = '\0';
      //data[0] = i;
      //data[1] = i+1;
      chibiTx(addr, data, 5);
      delay(10);
    }
}


/**************************************************************************/
/*!
    Concatenate multiple strings from the command line starting from the
    given index into one long string separated by spaces.
*/
/**************************************************************************/
int strCat(char *buf, unsigned char index, char arg_cnt, char **args)
{
    uint8_t i, len;
    char *data_ptr;

    data_ptr = buf;
    for (i=0; i<arg_cnt - index; i++)
    {
        len = strlen(args[i+index]);
        strcpy((char *)data_ptr, (char *)args[i+index]);
        data_ptr += len;
        *data_ptr++ = ' ';
    }
    *data_ptr++ = '\0';

    return data_ptr - buf;
}

/**************************************************************************/
// This is to implement the printf function from within arduino
/**************************************************************************/
static int uart_putchar (char c, FILE *stream)
{
    Serial.write(c);
    return 0;
}



