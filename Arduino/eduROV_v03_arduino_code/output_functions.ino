// Output settings
int vertical = 0;
int starboard = 0;
int port = 0;
int lights = 0;

// Output handler function, implements soft PWM across all motor outputs
void updateOutput() {
  int period = (millis() % 1000) / 10;
  static bool vertical_active   = false;
  static bool port_active       = false;
  static bool starboard_active  = false;

  if (period == 0)
  {
    if (vertical != 0)
    {
      digitalWrite(ch1a, vertical  >= 0 ? LOW : HIGH);
      digitalWrite(ch2a, vertical  >= 0 ? LOW : HIGH);
      vertical_active   = true;
      Serial.println(String("t:") + period + " Enable vertical channels"); 
    }
    if (starboard != 0) {
      digitalWrite(ch3a, starboard >= 0 ? LOW : HIGH);
      starboard_active  = true;      
    }
    if (port != 0) {
      digitalWrite(ch4a, port      >= 0 ? LOW : HIGH);
      port_active       = true;
    }
    
  }

  if (vertical_active && period > abs(vertical)) {
    digitalWrite(ch1a, vertical  >= 0 ? HIGH : LOW);
    digitalWrite(ch2a, vertical  >= 0 ? HIGH : LOW);
    vertical_active = false;
    Serial.println(String("t:") + period + " Lower Vertical channel");
  }

  if (starboard_active && period > abs(starboard)) {
    digitalWrite(ch3a, starboard >= 0 ? HIGH : LOW);
    starboard_active = false;
  }

  if (port_active && period > abs(port)) {
    digitalWrite(ch4a, port >= 0 ? HIGH : LOW);
    port_active = false;
  }
}

void setOutput(String msg) {
  // expects a 4 digit string, values 0, 1 or 2

  noInterrupts();
  sscanf(msg.c_str(), "vertical=%i;starboard=%i;port=%i;lights=%i", &vertical, &starboard, &port, &lights);

  //Diving/rising motors
  //Run two motors in sync
  if (vertical > 1) {
    digitalWrite(ch1a, LOW);
    digitalWrite(ch1b, LOW);
    digitalWrite(ch2a, LOW);
    digitalWrite(ch2b, LOW);
  } else if (vertical < -1) {
    digitalWrite(ch1a, HIGH);
    digitalWrite(ch1b, HIGH);
    digitalWrite(ch2a, HIGH);
    digitalWrite(ch2b, HIGH);
  } else {
    vertical = 0;
    digitalWrite(ch1a, LOW);
    digitalWrite(ch1b, LOW);
    digitalWrite(ch2a, LOW);
    digitalWrite(ch2b, LOW);
  }

  //Port side motor
  if(port > 1){
    digitalWrite(ch3a, LOW);
    digitalWrite(ch3b, LOW);
  }else if(port < -1){
    digitalWrite(ch3a, HIGH);
    digitalWrite(ch3b, HIGH);
  }else{
    digitalWrite(ch3a, LOW);
    digitalWrite(ch3b, LOW);
  }
  //Starboard motor
  if(starboard > 1){
    digitalWrite(ch4a, LOW);
    digitalWrite(ch4b, LOW);
  }else if(starboard < -1){
    digitalWrite(ch4a, HIGH);
    digitalWrite(ch4b, HIGH);
  }else{
    digitalWrite(ch4a, LOW);
    digitalWrite(ch4b, LOW);
  }

  vertical  = constrain(vertical , -100, 100);
  port      = constrain(port     , -100, 100);
  starboard = constrain(starboard, -100, 100);

  Timer1.restart();
  interrupts();

  //LED lights
  if(lights){
    digitalWrite(ledPin, HIGH);
  }else{
    digitalWrite(ledPin, LOW);
  }
}
