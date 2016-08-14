#define trigPin 5
#define echoPin 7
#define awakePin 10
#define led 13

void setup() {
  Serial.begin (57600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(awakePin, OUTPUT);
  pinMode(led, OUTPUT);
  digitalWrite(awakePin, HIGH);
}

void loop() {
  int32_t duration, distance;
  digitalWrite(trigPin, LOW);  // Added this line
  delayMicroseconds(2); // Added this line
  digitalWrite(trigPin, HIGH);
//  delayMicroseconds(1000); - Removed this line
  delayMicroseconds(10); // Added this line
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  Serial.println(distance);
  if (distance >= 200){
    distance = 200;
  }
  if (distance < 0){
    distance = 0;
  }
  
  digitalWrite(led, HIGH);
  delay(distance*10);
  digitalWrite(led, LOW);
  
  delay(500);
} 
