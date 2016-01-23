// #include <map>
#include "sensors.h"
#include <chibi.h>
#include <utilsawesome.h>



#include <NewPing.h>
Paralax28015REVC_Sensor::Paralax28015REVC_Sensor(unsigned int sensor_id, int sonar_pin):BaseSensor(sensor_id){
	this->sonar = new NewPing(sonar_pin, sonar_pin, 200);
};

double Paralax28015REVC_Sensor::read(unsigned char *buffer){
	float distance = (float) sonar->ping() / US_ROUNDTRIP_CM; 
	// Serial.print("DISTANCE: ");
 //  Serial.println(distance);
  if (distance > 0){
		// Reading dist = {"distance", distance, millis()};
		// append_reading_to_buffer(buffer, dist);
	}
};


BaseSensor::BaseSensor(unsigned int sensor_id){
  this->sensor_id = sensor_id;
}

void read_battery_voltage(unsigned char *buffer, int battery_voltage_pin, float reference_voltage){
  unsigned int vbat = analogRead(battery_voltage_pin);
  double batt = ((vbat/1023.0) * reference_voltage) * 2;
  // Reading battery_voltage = {"vbat", batt, millis()};
  // append_reading_to_buffer(buffer, battery_voltage);
}



DHT_V12_Sensor::DHT_V12_Sensor(unsigned int temp_id, unsigned int hum_id, unsigned char signal_pin):BaseSensor(sensor_id){
	this->measurements = new std::map<int,double>;
  this->sensor = new dht();
  this->temp_id = temp_id;
  this->hum_id = hum_id;
}

double DHT_V12_Sensor::read(unsigned char *buffer){
  // Serial.println("AAAAAAAAAA");
  // float temperature = this->sensor->temperature;  
  // return this->sensor->temperature;  
  // if (temperature > 0) {
  //   Reading temp = {"temperature", temperature, millis()};
  //   append_reading_to_buffer(buffer, temp);
  // }

  // float humidity = this->sensor->humidity;
  // if (humidity > 0) {
    // Reading hum = {"humidity", humidity , millis()};
    // append_reading_to_buffer(buffer, hum);
  // }
  return 2.1;
}

std::map<int,double> DHT_V12_Sensor::read(){
  std::map<int,double> measurements;
  measurements[this->temp_id] = 2.3;
  return measurements;
}



