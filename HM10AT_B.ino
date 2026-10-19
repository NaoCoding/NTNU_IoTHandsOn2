#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX

void setup() {
  // 啟動串行通信，等待端口連接：
  Serial.begin(9600);
  while (!Serial) {
    ; // 等待串行端口連接，僅在原生 USB 端口需要
  }

  Serial.println("串行通信已啟動！");

  // 設定 SoftwareSerial 的數據速率
  mySerial.begin(9600);
  // mySerial.println("AT\r\n");  // 已註解：連線中送 AT 會讓 HM-10 斷線
  Serial.println("將發送 AT 指令");
}

void loop() { // 不斷運行
  // 檢查 SoftwareSerial 是否有可用數據
  if (mySerial.available()) {
    String response = mySerial.readString(); // 讀取回應
    Serial.println(response); // 將回應顯示在串行監控器
  }

  // 檢查是否有來自串行監控器的輸入
  if (Serial.available()) {
    mySerial.write(Serial.read()); // 將輸入發送到 HM-10
  }
}