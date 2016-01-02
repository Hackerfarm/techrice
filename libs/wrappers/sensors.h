#include <NewPing.h>

class BaseSensor{
	public: 
		BaseSensor(unsigned int sensor_id);
		unsigned int sensor_id;
		unsigned int n_values;
		virtual double read(unsigned char *buffer) = 0;
};

class Paralax28015REVC_Sensor:public BaseSensor{
	private: 
		NewPing *sonar; // Sonar is a pointer that points to a NewPing instance
	
	public:
		Paralax28015REVC_Sensor(unsigned int sensor_id, int sonar_pin);
		double read(unsigned char *buffer);
};

#include "DHT.h"
// #define DHTTYPE DHT11   // Type of DHT sensor, in our case we are using DHT11
// #define DHT11_PIN A0    // Pin where the DHT11 is connected
// dht DHT;

class DHT_V12_Sensor:public BaseSensor{
	private:
		dht *sensor;
	public:
		DHT_V12_Sensor(unsigned int sensor_id, unsigned char signal_pin);
		double read(unsigned char *buffer);
};


void read_battery_voltage(unsigned char *buffer, int battery_voltage_pin, float reference_voltage);