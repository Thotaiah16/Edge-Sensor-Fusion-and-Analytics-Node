import os


def getenv(key, default):
    value = os.getenv(key)
    return value if value is not None and value != "" else default


SENSOR_MODE = getenv("SENSOR_MODE", "mock")
PUBLISH_INTERVAL_SEC = float(getenv("PUBLISH_INTERVAL_SEC", "1.0"))

I2C_BUS = int(getenv("I2C_BUS", "1"))
IMU_ADDRESS = int(getenv("IMU_ADDRESS", "0x68"), 16)

SPI_BUS = int(getenv("SPI_BUS", "0"))
SPI_DEVICE = int(getenv("SPI_DEVICE", "0"))

MQTT_HOST = getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(getenv("MQTT_PORT", "8883"))
MQTT_TOPIC = getenv("MQTT_TOPIC", "edge/sensor/fused")
MQTT_TLS_CA = getenv("MQTT_TLS_CA", "")
MQTT_TLS_CERT = getenv("MQTT_TLS_CERT", "")
MQTT_TLS_KEY = getenv("MQTT_TLS_KEY", "")
MQTT_TLS_INSECURE = getenv("MQTT_TLS_INSECURE", "false").lower() == "true"

MQTT_USERNAME = getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = getenv("MQTT_PASSWORD", "")
