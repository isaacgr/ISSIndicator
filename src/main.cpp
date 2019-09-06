#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

WiFiClient client;
HTTPClient http;

void setup()
{
  Serial.begin(115200);
  WiFi.begin("VIRGIN559", "412C7934");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.println("Waiting for connection");
  }
}

void loop()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    http.begin("http://api.open-notify.org/iss-now.json");
    /*
      {
      message: "success",
      iss_position: {
        latitude: "-40.5581",
        longitude: "-162.1823"
      },
      timestamp: 1567473121
      }
    */
    int httpCode = http.GET();
    if (httpCode > 200)
    {
      const size_t capacity = JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(3) + 90;
      DynamicJsonDocument jsonBuffer(capacity);
      JsonObject &root = jsonBuffer.parseObject(http.getString());
      const char *message = jsonBuffer["message"];
      const char *iss_position_latitude = jsonBuffer["iss_position"]["latitude"];
      const char *iss_position_longitude = jsonBuffer["iss_position"]["longitude"];
      long timestamp = jsonBuffer["timestamp"];
      Serial.println(iss_position_latitude);
      Serial.println(iss_position_longitude);
      Serial.println(timestamp);
    }
    http.end();
  }
  delay(5000);
}