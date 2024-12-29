#include <DHT.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define DHTPIN 14
#define DHTTYPE DHT22

#define REF_COMM_TEMP "ESP8266_TEMP_DHT22"
#define REF_COMM_HUM "ESP8266_HUM_DHT22"
#define REF_COMM_LUM "ESP8266_LUM_MLG5516B"
#define ID_CAPTEUR_TEMP "1001"
#define ID_CAPTEUR_HUM "1002"
#define ID_CAPTEUR_LUM "1000"

const char* ssid = "HerveNet";
const char* password = "radioactivity";

DHT dht(DHTPIN, DHTTYPE);

void connectToWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.println("Connecté au wifi");
}

void readSensorAndSendData() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  Serial.printf("t: '%.2f' h: '%.2f'\n", temperature, humidity);

  if (isnan(humidity) || isnan(temperature)) {
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    WiFiClient client;

    StaticJsonDocument<200> jsonDoc_temp;
    jsonDoc_temp["id_capteur"] = ID_CAPTEUR_TEMP;
    jsonDoc_temp["ref_comm"] = REF_COMM_TEMP;
    jsonDoc_temp["value"] = temperature;

    char jsonBuffer_temp[512];
    serializeJson(jsonDoc_temp, jsonBuffer_temp);

    http.begin(client, "http://192.168.1.16:8000/api/capteur");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonBuffer_temp);
    Serial.printf("Reponse du serveur : '%i'\n", httpResponseCode);
    http.end();


    StaticJsonDocument<200> jsonDoc_hum;
    jsonDoc_hum["id_capteur"] = ID_CAPTEUR_HUM;
    jsonDoc_hum["ref_comm"] = REF_COMM_HUM;
    jsonDoc_hum["value"] = humidity;

    char jsonBuffer_hum[512];
    serializeJson(jsonDoc_hum, jsonBuffer_hum);

    http.begin(client, "http://192.168.1.16:8000/api/capteur");
    http.addHeader("Content-Type", "application/json");
    httpResponseCode = http.POST(jsonBuffer_hum);
    Serial.printf("Reponse du serveur : '%i'\n", httpResponseCode);
    http.end();
  }
}

void getLedState() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, "http://192.168.1.16:8000/api/acctionneur/led_state");
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
      digitalWrite(LED_BUILTIN, response == "true" ? LOW : HIGH);
    }
    // Serial.print("Demande de l'état de la LED : ");
    // Serial.println(http.getString());
    http.end();
  }
}

void getToneState() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, "http://192.168.1.16:8000/api/acctionneur/tone");
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
      if(response == "true")
        tone(8, 440, 1000);
    }
    // Serial.print("Demande de l'état de la LED : ");
    // Serial.println(http.getString());
    http.end();
  }
}

const int adcPin = A0;     // Pin où l'ADC est connecté
const float vin = 3.3;     // Tension d'alimentation du pont diviseur (en volts)
const float r2 = 10000;    // Résistance fixe du pont diviseur (en ohms)
const float k = 1500000;      // Constante caractéristique de la photorésistance (en ohms)
const float n = 1.0;       // Exposant caractéristique de la photorésistance

void readLightAndSendData(void) {
  // Lire la valeur de l'ADC
  int adcValue = analogRead(adcPin);
  
  // Calcul de la tension de sortie (Vout) en fonction de l'ADC
  float vout = adcValue * (vin / 1024.0);

  // Calcul de la résistance de la photorésistance (RL)
  float rl = r2 * (vin / vout - 1);

  // Calcul de l'éclairement en lux
  float lux = k / pow(rl, n);
 
  // print the readings in the Serial Monitor
  Serial.print("lux = ");
  Serial.println(lux);

  HTTPClient http;
    WiFiClient client;

    StaticJsonDocument<200> jsonDoc_temp;
    jsonDoc_temp["id_capteur"] = ID_CAPTEUR_LUM;
    jsonDoc_temp["ref_comm"] = REF_COMM_LUM;
    jsonDoc_temp["value"] = lux;

    char jsonBuffer_temp[512];
    serializeJson(jsonDoc_temp, jsonBuffer_temp);

    http.begin(client, "http://192.168.1.16:8000/api/capteur");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonBuffer_temp);
    Serial.printf("Reponse du serveur : '%i'\n", httpResponseCode);
    http.end();
}

void setup() {
  Serial.begin(9600);
  Serial.setDebugOutput(true);
  pinMode(LED_BUILTIN, OUTPUT);
  dht.begin();
  connectToWiFi();
}

void loop() {
  readSensorAndSendData();
  readLightAndSendData();
  delay(30000);
}
