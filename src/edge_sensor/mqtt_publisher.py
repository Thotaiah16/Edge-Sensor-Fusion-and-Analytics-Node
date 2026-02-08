import json
import ssl
import time

import paho.mqtt.client as mqtt

from . import config


class MqttPublisher:
    def __init__(self):
        self._client = mqtt.Client()
        self._connected = False

        if config.MQTT_USERNAME:
            self._client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

        if config.MQTT_TLS_CA:
            self._client.tls_set(
                ca_certs=config.MQTT_TLS_CA,
                certfile=config.MQTT_TLS_CERT or None,
                keyfile=config.MQTT_TLS_KEY or None,
                tls_version=ssl.PROTOCOL_TLS_CLIENT,
            )
            self._client.tls_insecure_set(config.MQTT_TLS_INSECURE)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def connect(self):
        self._client.connect(config.MQTT_HOST, config.MQTT_PORT, keepalive=60)
        self._client.loop_start()

        timeout = time.time() + 10
        while not self._connected and time.time() < timeout:
            time.sleep(0.1)

        if not self._connected:
            raise RuntimeError("Failed to connect to MQTT broker")

    def publish(self, payload):
        result = self._client.publish(config.MQTT_TOPIC, json.dumps(payload), qos=1)
        result.wait_for_publish(timeout=5)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed with rc={result.rc}")

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
