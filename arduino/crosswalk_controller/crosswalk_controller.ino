// Crosswalk Controller - Edge B (Arduino)
// Traffic light state machine with serial command interface

// Pin definitions
const int PIN_RED = 2;
const int PIN_YEL = 3;
const int PIN_GRN = 4;
const int PIN_WALK = 5;
const int PIN_BTN = 6;

// State machine states
enum State { IDLE_GREEN, YELLOW, RED_WAIT, WALK, COOLDOWN };
State state = IDLE_GREEN;

unsigned long stateStart = 0;

// Timing durations (ms)
const unsigned long T_YELLOW = 2000;
const unsigned long T_RED_WAIT = 1000;
const unsigned long T_WALK = 6000;
const unsigned long T_COOLDOWN = 4000;

bool requested = false;

void setLights(bool r, bool y, bool g, bool w) {
  digitalWrite(PIN_RED, r);
  digitalWrite(PIN_YEL, y);
  digitalWrite(PIN_GRN, g);
  digitalWrite(PIN_WALK, w);
}

void goState(State s) {
  state = s;
  stateStart = millis();

  // Publish state back over serial so laptop can log it
  switch (state) {
    case IDLE_GREEN: Serial.println("STATE=IDLE_GREEN"); setLights(0,0,1,0); break;
    case YELLOW:     Serial.println("STATE=YELLOW");     setLights(0,1,0,0); break;
    case RED_WAIT:   Serial.println("STATE=RED_WAIT");   setLights(1,0,0,0); break;
    case WALK:       Serial.println("STATE=WALK");       setLights(1,0,0,1); break;
    case COOLDOWN:   Serial.println("STATE=COOLDOWN");   setLights(0,0,1,0); break;
  }
}

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_YEL, OUTPUT);
  pinMode(PIN_GRN, OUTPUT);
  pinMode(PIN_WALK, OUTPUT);
  pinMode(PIN_BTN, INPUT_PULLUP);

  Serial.begin(115200);
  goState(IDLE_GREEN);
}

void loop() {
  // Manual request button (pressed = LOW due to INPUT_PULLUP)
  if (digitalRead(PIN_BTN) == HIGH) {
    requested = true;
    Serial.println("EVENT=BUTTON_REQUEST");
    delay(200); // Simple debounce
  }

  // Serial command request from laptop
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "START") {
      requested = true;
      Serial.println("EVENT=REMOTE_REQUEST");
    }
  }

  unsigned long elapsed = millis() - stateStart;

  // State machine logic
  switch (state) {
    case IDLE_GREEN:
      if (requested) {
        requested = false;
        goState(YELLOW);
      }
      break;

    case YELLOW:
      if (elapsed >= T_YELLOW) goState(RED_WAIT);
      break;

    case RED_WAIT:
      if (elapsed >= T_RED_WAIT) goState(WALK);
      break;

    case WALK:
      if (elapsed >= T_WALK) goState(COOLDOWN);
      break;

    case COOLDOWN:
      if (elapsed >= T_COOLDOWN) goState(IDLE_GREEN);
      break;
  }
}

