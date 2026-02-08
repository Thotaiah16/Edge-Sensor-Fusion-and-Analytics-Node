FROM debian:bookworm-slim AS builder

ARG MOSQUITTO_VERSION=2.0.22

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        libssl-dev \
        libuv1-dev \
        libwrap0-dev \
        uuid-dev \
        xsltproc \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/mosquitto.tar.gz \
        https://github.com/eclipse/mosquitto/archive/refs/tags/v${MOSQUITTO_VERSION}.tar.gz \
    && tar -xzf /tmp/mosquitto.tar.gz -C /tmp \
    && cmake -S /tmp/mosquitto-${MOSQUITTO_VERSION} -B /tmp/mosquitto-build \
        -DWITH_CJSON=ON \
        -DWITH_DOCS=OFF \
        -DWITH_MANPAGES=OFF \
        -DWITH_WEBSOCKETS=OFF \
    && cmake --build /tmp/mosquitto-build \
    && cmake --install /tmp/mosquitto-build \
    && rm -rf /tmp/mosquitto.tar.gz /tmp/mosquitto-${MOSQUITTO_VERSION} /tmp/mosquitto-build

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libssl3 \
        libuv1 \
        libwrap0 \
        libcjson1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --system --home /mosquitto --shell /usr/sbin/nologin mosquitto \
    && mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log \
    && chown -R mosquitto:mosquitto /mosquitto

COPY --from=builder /usr/local/sbin/mosquitto /usr/local/sbin/mosquitto
COPY --from=builder /usr/local/sbin/mosquitto_ctrl /usr/local/sbin/mosquitto_ctrl
COPY --from=builder /usr/local/sbin/mosquitto_passwd /usr/local/sbin/mosquitto_passwd
COPY --from=builder /usr/local/lib/libmosquitto.so* /usr/local/lib/

ENV LD_LIBRARY_PATH=/usr/local/lib

USER mosquitto
WORKDIR /mosquitto
