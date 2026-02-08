FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update \
	&& apt-get upgrade -y \
	&& rm -rf /var/lib/apt/lists/* \
	&& python -m pip install --no-cache-dir --upgrade pip setuptools "wheel>=0.46.2" \
	&& pip install --no-cache-dir --prefix /install -r requirements.txt

COPY src ./src

FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app/src ./src

ENV SENSOR_MODE=mock
ENV MQTT_HOST=mosquitto
ENV MQTT_PORT=8883
ENV MQTT_TOPIC=edge/sensor/fused
ENV PUBLISH_INTERVAL_SEC=1.0
ENV PYTHONPATH=/app/src:/usr/local/lib/python3.11/site-packages

CMD ["-m", "edge_sensor.main"]
