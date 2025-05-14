#include <LiquidCrystal.h>

LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// Данные с ПК
float cpu, ram, gpuLoad, gpuTemp, fanSpeed, download, upload;

// Настройки меню
const int SCREEN_COUNT = 3;
int currentScreen = 1;
unsigned long lastSwitchTime = 0;
const unsigned long SWITCH_INTERVAL = 10000;

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.print("System Monitor");
  delay(2000);
  lcd.clear();
}

void loop() {
  // Получение данных
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    parseData(data);
  }

  // Обработка кнопок
  handleButtons();

  // Отображение
  updateDisplay();
  delay(100);
}

void parseData(String data) {
  int indices[6];
  int lastIndex = 0;
  
  for (int i = 0; i < 6; i++) {
    indices[i] = data.indexOf(',', lastIndex);
    lastIndex = indices[i] + 1;
  }
  
  cpu = data.substring(0, indices[0]).toFloat();
  ram = data.substring(indices[0]+1, indices[1]).toFloat();
  gpuLoad = data.substring(indices[1]+1, indices[2]).toFloat();
  gpuTemp = data.substring(indices[2]+1, indices[3]).toFloat();
  fanSpeed = data.substring(indices[3]+1, indices[4]).toFloat();
  download = data.substring(indices[4]+1, indices[5]).toFloat();
  upload = data.substring(indices[5]+1).toFloat();
}

void handleButtons() {
  int btn = analogRead(0);
  
  if (btn < 50) {       // Left
    currentScreen = (currentScreen - 2 + SCREEN_COUNT) % SCREEN_COUNT + 1;
    lastSwitchTime = millis();
    Serial.println("LEFT");
  }
  else if (btn < 200) { // Right
    currentScreen = currentScreen % SCREEN_COUNT + 1;
    lastSwitchTime = millis();
    Serial.println("RIGHT");
  }
}

void updateDisplay() {
  lcd.clear();
  
  switch (currentScreen) {
    case 1:
      lcd.setCursor(0, 0);
      lcd.print("CPU:");
      lcd.print(cpu, 1);
      lcd.print("% R:");
      lcd.print(ram, 1);
      lcd.print("%");
      
      lcd.setCursor(0, 1);
      lcd.print("GPU:");
      lcd.print(gpuLoad, 1);
      lcd.print("% ");
      lcd.print(gpuTemp, 1);
      lcd.print((char)223);
      lcd.print("C");
      break;
      
    case 2:
      lcd.setCursor(0, 0);
      lcd.print("Fan Speed");
      lcd.setCursor(0, 1);
      lcd.print("GPU:");
      lcd.print(fanSpeed, 1);
      lcd.print("% CPU:");
      lcd.print(cpu/10, 1); // Примерная скорость CPU fan
      lcd.print("%");
      break;
      
    case 3:
      lcd.setCursor(0, 0);
      lcd.print("Network");
      lcd.setCursor(0, 1);
      lcd.print("D:");
      lcd.print(download, 1);
      lcd.print(" U:");
      lcd.print(upload, 1);
      lcd.print(" KB/s");
      break;
  }
}