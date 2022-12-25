// Reference:
// https://github.com/Seeed-Studio/Grove_EMG_detector_demo_code/blob/master/Grove_EMG_detector_demo_code.ino

int GetAnalog() {
  const int n = 1 << 5;
  long sum = 0;
  for (int i = 0; i < n; i++) {
    sum += analogRead(A0);
  }
  return sum / n;
}

void setup() { Serial.begin(115200); }

void loop() {
  Serial.println(GetAnalog());
  delay(10);
}
