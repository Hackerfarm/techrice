#include <chibi.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h> 
#include "src/chb_drvr.h"

unsigned char buf[100];
int len;
int dupe_cnt = 0;
unsigned char old[100];

static FILE uartout = {0};         

/**************************************************************************/
/*!

*/
/**************************************************************************/
void setup()
{ 
    // fill in the UART file descriptor with pointer to writer.
  fdev_setup_stream (&uartout, uart_putchar, NULL, _FDEV_SETUP_WRITE);
  
  // The uart is the standard output device STDOUT.
  stdout = &uartout ;
  
  pinMode(31, OUTPUT);
  digitalWrite(31, HIGH);
  
  chibiCmdInit(57600);
  chibiInit();
  
  // full power on transceiver
  //chibiRegWrite(0x5, 0xE1);

  //chibiRegWrite(XOSC_CTRL, 0xFA);

  old[0] = 3;

  chibiCmdAdd("rd", cmd_reg_read);
  chibiCmdAdd("wr", cmd_reg_write);
  chibiCmdAdd("mrd", cmdMcuReadReg);
  chibiCmdAdd("mwr", cmdMcuWriteReg);
  chibiCmdAdd("getsaddr", cmd_get_short_addr);
  chibiCmdAdd("setsaddr", cmd_set_short_addr);
  chibiCmdAdd("setrate", cmd_setrate);
  chibiCmdAdd("setchannel", cmd_setChannel);
  chibiCmdAdd("setmode", cmd_setMode);
  chibiCmdAdd("slr", cmdSleepRadio);
  chibiCmdAdd("slm", cmdSleepMcu);
  chibiCmdAdd("hgm", cmd_setHGM);
  chibiCmdAdd("send", cmd_tx);
  chibiCmdAdd("send2", cmd_tx2);  
  
  // for visionarity board
  //DDRC |= 1<<6;
  //PORTC |= 1<<6;
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void loop()
{
  chibiCmdPoll();
 /*
   // Check if any data was received from the radio. If so, then handle it.
  if (chibiDataRcvd() == true)
  { 
    int len, rssi, src_addr;
    byte buf2[100];  // this is where we store the received data
    
    // retrieve the data and the signal strength
    len = chibiGetData(buf2);
    rssi = chibiGetRSSI();
    src_addr = chibiGetSrcAddr();
    
    // Print out the message and the signal strength
    Serial.print("Message received from node 0x");
    Serial.print(src_addr, HEX);
    Serial.print(": "); 
    Serial.print((char *)buf2); 
    Serial.print(", RSSI = 0x"); Serial.println(rssi, HEX);
  }
 */
 
 
  if (chibiDataRcvd() == true)
  { 
    int rssi, src_addr;
    len = chibiGetData(buf);
    if (len == 0) return;
    
    // retrieve the data and the signal strength
    rssi = chibiGetRSSI();
    src_addr = chibiGetSrcAddr();
    
    // Print out the message and the signal strength
 /*   Serial.print("Message received from node 0x");
    Serial.print(src_addr, HEX);
    Serial.print(": "); 
    Serial.print((char *)buf); 
    Serial.print(", RSSI = 0x"); Serial.println(rssi, HEX);
 */
//  }   
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
    printf("Write: %04X, %02X.\n", addr, val);

    val = chibiRegRead(addr);
    printf("Readback: %04X, %02X.\n", addr, val);
}

/**************************************************************************/
/*!
    Read regs
*/
/**************************************************************************/
void cmdMcuReadReg(int arg_cnt, char **args)
{
  unsigned char addr, val;
  
  addr = chibiCmdStr2Num(args[1], 16);

  val = *(volatile unsigned char *)addr;
  printf("Addr %02X = %02X\n", addr, val);
}

/**************************************************************************/
/*!
    Write regs
*/
/**************************************************************************/
void cmdMcuWriteReg(int arg_cnt, char **args)
{
  unsigned char addr, val;
  
  addr = chibiCmdStr2Num(args[1], 16);
  val = chibiCmdStr2Num(args[2], 16);
  
  *(volatile unsigned char *)addr = val;
  
  val = *(volatile unsigned char *)addr;
  printf("Addr %02X = %02X.\n", addr, val);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmd_get_short_addr(int arg_cnt, char **args)
{
  int val;
  
  val = chibiGetShortAddr();
  sprintf((char *)buf, "Short Address: %04X.\n\r", val);
  Serial.print((char *)buf);
}

void cmd_set_short_addr(int arg_cnt, char **args)
{
  int val;
  
  val = chibiCmdStr2Num(args[1], 16);
  chibiSetShortAddr(val);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmd_setrate(int arg_cnt, char **args)
{
    uint8_t rate;
    rate = chibiCmdStr2Num(args[1], 10);
    chibiSetDataRate(rate);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmd_setChannel(int arg_cnt, char **args)
{
    uint8_t channel;
    channel = chibiCmdStr2Num(args[1], 10);
    chibiSetChannel(channel);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmd_setMode(int arg_cnt, char **args)
{
    uint8_t mode;
    mode = chibiCmdStr2Num(args[1], 10);
    chibiSetMode(mode);
}

/**************************************************************************/
/*!

*/
/**************************************************************************/
void cmd_setHGM(int arg_cnt, char **args)
{
#if 0
    uint8_t hgm;
    hgm = chibiCmdStr2Num(args[1], 10);
    if (hgm) chibiHighGainModeEnable();
    else chibiHighGainModeDisable();
#endif
}

/**************************************************************************/
// 
/**************************************************************************/
void cmdSleepMcu(int arg_cnt, char **args)
{
  //  pinMode(slTrPin, INPUT);
  //  digitalWrite(slTrPin, HIGH);
  
    
  // disable UART
  UCSR0B = 0x00;
  
  // set all inputs
  PORTC = 0x00;
  DDRC = 0x00; 
  
  PORTD = 0x00;
  DDRD = 0x00;
  
  printf("Sleeping MCU\n");
  delay(100);
  
  ADCSRA &= ~(1 << ADEN);    // Disable ADC
  
  // write sleep mode
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();                       // setting up for sleep ...
  sleep_mode();
}

/**************************************************************************/
// 
/**************************************************************************/
void cmdSleepRadio(int arg_cnt, char **args)
{
  int val = strtol(args[1], NULL, 10);
  
  // turn off high gain mode
  //chibiHighGainModeDisable();
  //delay(10);
  
  // turn on/off radio
  chibiSleepRadio(val);
  
  PORTB = 0; // force all port b pins low
  DDRB = 0;  // turn all port b pins to input
}

/**************************************************************************/
/*!
    Transmit data to another node wirelessly using Chibi stack.
    Usage: send <addr> <string...>
*/
/**************************************************************************/
void cmd_tx(int arg_cnt, char **args)
{
    char data[100];
    int addr, len;

    addr = chibiCmdStr2Num(args[1], 16);
    len = strCat(data, 2, arg_cnt, args); 
    chibiTx(addr, (uint8_t *)data,len);
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
    
    for (i=0; i<200; i++)
    {
      sprintf((char *)data, "%03d", i);
      data[3] = '\0';
      //data[0] = i;
      //data[1] = i+1;
      chibiTx(addr, data, 4);
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
