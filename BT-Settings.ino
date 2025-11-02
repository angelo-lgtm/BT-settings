#include <SoftwareSerial.h>
const int joyXPin = A0;
const int joyYPin = A1;
const int buttonPin = 2;
// SoftwareSerial(rxPin, txPin)
SoftwareSerial bt(10, 11);  // RX=10, TX=11
void setup() {
  Serial.begin(9600);   // for debugging on USB serial monitor
  bt.begin(9600);       // for Bluetooth
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.println("Bluetooth joystick ready!");
}
void loop() {
  int joyX = analogRead(joyXPin);
  int joyY = analogRead(joyYPin);
  int buttonState = digitalRead(buttonPin);
  // Send data to Bluetooth
  bt.print(joyX);
  bt.print(",");
  bt.print(joyY);
  bt.print(",");
  bt.println(buttonState);
  // Optional: Debug output to Serial Monitor
  Serial.print(joyX);
  Serial.print(",");
  Serial.print(joyY);
  Serial.print(",");
  Serial.println(buttonState);
  delay(100);
}