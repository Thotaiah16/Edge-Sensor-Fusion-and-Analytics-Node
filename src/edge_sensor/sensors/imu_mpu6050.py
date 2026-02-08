import math
import random
import time

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None


class IMUSensor:
    def __init__(self, mode, bus_id=1, address=0x68):
        self.mode = mode
        self.bus_id = bus_id
        self.address = address
        self._start = time.time()
        self._bus = None

        if self.mode == "hardware":
            if SMBus is None:
                raise RuntimeError("smbus2 not available for hardware mode")
            self._bus = SMBus(self.bus_id)
            self._initialize_device()

    def _initialize_device(self):
        # Wake up the MPU6050
        self._bus.write_byte_data(self.address, 0x6B, 0)

    def read(self):
        if self.mode == "hardware":
            return self._read_hardware()
        return self._read_mock()

    def _read_hardware(self):
        # Read raw accelerometer and gyro registers
        accel_x = self._read_word(0x3B) / 16384.0
        accel_y = self._read_word(0x3D) / 16384.0
        accel_z = self._read_word(0x3F) / 16384.0

        gyro_x = self._read_word(0x43) / 131.0
        gyro_y = self._read_word(0x45) / 131.0
        gyro_z = self._read_word(0x47) / 131.0

        return {
            "accel": {"x": accel_x, "y": accel_y, "z": accel_z},
            "gyro": {"x": gyro_x, "y": gyro_y, "z": gyro_z},
        }

    def _read_word(self, reg):
        high = self._bus.read_byte_data(self.address, reg)
        low = self._bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    def _read_mock(self):
        t = time.time() - self._start
        accel_x = 0.02 * math.sin(t) + random.uniform(-0.02, 0.02)
        accel_y = 0.02 * math.cos(t) + random.uniform(-0.02, 0.02)
        accel_z = 1.0 + random.uniform(-0.02, 0.02)

        gyro_x = 10.0 * math.sin(t) + random.uniform(-0.5, 0.5)
        gyro_y = 10.0 * math.cos(t) + random.uniform(-0.5, 0.5)
        gyro_z = random.uniform(-0.2, 0.2)

        return {
            "accel": {"x": accel_x, "y": accel_y, "z": accel_z},
            "gyro": {"x": gyro_x, "y": gyro_y, "z": gyro_z},
        }
