// Reference:
// https://github.com/Seeed-Studio/Grove_EMG_detector_demo_code/blob/master/Grove_EMG_detector_demo_code.ino

const int kNumSamples = 1 << 5;

int GetAnalog() {
  long sum = 0;
  for (int i = 0; i < kNumSamples; i++) {
    sum += analogRead(A0);
  }
  return sum / kNumSamples;
}

void setup() { Serial.begin(115200); }

void loop() {
  Serial.println(GetAnalog());
  delay(10);
}
