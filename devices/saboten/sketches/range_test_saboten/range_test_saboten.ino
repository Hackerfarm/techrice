#include <chibi.h>
#include <Wire.h>
#include <stdint.h>

int hgmPin = 22;
int ledPin = 18;
int vbatPin = 31;
int vsolPin = 29;
int led_state = 1;

#define ADCREFVOLTAGE 3.3
#define NODE_ID 300

void setup()
{    
	// set up high gain mode pin
  pinMode(hgmPin, OUTPUT);
  digitalWrite(hgmPin, LOW);
  
  // set up battery monitoring
  pinMode(vbatPin, INPUT);
  
  // set up LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Initialize the chibi command line and set the speed to 57600 bps
  chibiCmdInit(57600);
  
  // Initialize the chibi wireless stack
  chibiInit();
  
  // datecode version
  Serial.println("Range Test Saboten v0.1");

  // high gain mode
  digitalWrite(hgmPin, HIGH);

  
}

/**************************************************************************/
// Loop
/**************************************************************************/
void loop()
{
  static int count = 0;
	int32_t vbat;
	int32_t vsol;
  get_vbat(vbat);
  get_vsol(vsol);
  count++;

  char sbuf[1000];
  sprintf(sbuf, "COUNT:%d \tBAT: %d\tSOL:%d", 
                (int) count,
                (int) vbat, 
                (int) vsol);
  Serial.println(sbuf);
  chibiTx(BROADCAST_ADDR, (unsigned char*)(&sbuf), strlen(sbuf)+1);
  free(sbuf);
	led_state = 1-led_state;
	if(led_state==0)
		{ digitalWrite(ledPin, LOW); }
	else
		{ digitalWrite(ledPin, HIGH); }
	delay(1000);
}

// Gives a mV result
bool get_vbat(int32_t &battery)
{
  unsigned int vbat = analogRead(vbatPin);
  battery = (int32_t)(((vbat/1023.0) * ADCREFVOLTAGE) * 2000);
  return true;
}

// gives a mV result
bool get_vsol(int32_t &solar)
{
  unsigned int vsol = analogRead(vsolPin);
  solar = (int32_t)(((vsol/1023.0) * ADCREFVOLTAGE) * 2000);
}

/**************************************************************************/
// This is to implement the printf function from within arduino
/**************************************************************************/
static int uart_putchar (char c, FILE *stream)
{
    Serial.write(c);
    return 0;
}



