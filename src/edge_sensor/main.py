import json
import logging
import time
from datetime import datetime, timedelta, timezone

from . import config
from .fusion.kalman import KalmanAngle, accel_to_angles
from .mqtt_publisher import MqttPublisher
from .sensors.imu_mpu6050 import IMUSensor
from .sensors.temp_spi import TemperatureSensor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edge_sensor.main")


def build_payload(roll, pitch, temperature_c, accel, gyro):
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    ist_timestamp = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S IST")
    return {
        "timestamp": ist_timestamp,
        "roll": round(roll, 2),
        "pitch": round(pitch, 2),
        "temperature_c": round(temperature_c, 2),
        "accel": accel,
        "gyro": gyro,
    }


def main():
    logger.info("Starting in %s mode", config.SENSOR_MODE)

    imu = IMUSensor(config.SENSOR_MODE, config.I2C_BUS, config.IMU_ADDRESS)
    temp = TemperatureSensor(config.SENSOR_MODE, config.SPI_BUS, config.SPI_DEVICE)

    kalman_roll = KalmanAngle()
    kalman_pitch = KalmanAngle()

    mqtt = MqttPublisher()
    mqtt.connect()
    logger.info("Connected to MQTT broker")

    last_time = time.time()
    try:
        while True:
            now = time.time()
            dt = max(now - last_time, 0.001)
            last_time = now

            reading = imu.read()
            accel = reading["accel"]
            gyro = reading["gyro"]

            roll_accel, pitch_accel = accel_to_angles(accel)
            roll = kalman_roll.update(roll_accel, gyro["x"], dt)
            pitch = kalman_pitch.update(pitch_accel, gyro["y"], dt)

            temperature_c = temp.read_celsius()

            payload = build_payload(roll, pitch, temperature_c, accel, gyro)
            mqtt.publish(payload)
            logger.info("Published: %s", json.dumps(payload))

            time.sleep(config.PUBLISH_INTERVAL_SEC)
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        mqtt.disconnect()


if __name__ == "__main__":
    main()
