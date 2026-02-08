import math
import random
import time

try:
    import spidev
except ImportError:
    spidev = None


class TemperatureSensor:
    def __init__(self, mode, bus=0, device=0):
        self.mode = mode
        self.bus = bus
        self.device = device
        self._start = time.time()
        self._spi = None

        if self.mode == "hardware":
            if spidev is None:
                raise RuntimeError("spidev not available for hardware mode")
            self._spi = spidev.SpiDev()
            self._spi.open(self.bus, self.device)
            self._spi.max_speed_hz = 500000

    def read_celsius(self):
        if self.mode == "hardware":
            return self._read_hardware()
        return self._read_mock()

    def _read_hardware(self):
        # Example for MAX6675-style sensors
        raw = self._spi.readbytes(2)
        value = (raw[0] << 8) | raw[1]
        if value & 0x4:
            raise RuntimeError("Thermocouple open circuit")
        temp_c = (value >> 3) * 0.25
        return temp_c

    def _read_mock(self):
        t = time.time() - self._start
        base = 24.0 + 2.0 * math.sin(t / 10.0)
        return base + random.uniform(-0.2, 0.2)
