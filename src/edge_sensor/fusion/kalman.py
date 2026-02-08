import math


class KalmanAngle:
    def __init__(self, q_angle=0.001, q_bias=0.003, r_measure=0.03):
        self.q_angle = q_angle
        self.q_bias = q_bias
        self.r_measure = r_measure

        self.angle = 0.0
        self.bias = 0.0
        self.rate = 0.0

        self.p00 = 0.0
        self.p01 = 0.0
        self.p10 = 0.0
        self.p11 = 0.0

    def update(self, new_angle, new_rate, dt):
        self.rate = new_rate - self.bias
        self.angle += dt * self.rate

        self.p00 += dt * (dt * self.p11 - self.p01 - self.p10 + self.q_angle)
        self.p01 -= dt * self.p11
        self.p10 -= dt * self.p11
        self.p11 += self.q_bias * dt

        s = self.p00 + self.r_measure
        k0 = self.p00 / s
        k1 = self.p10 / s

        y = new_angle - self.angle
        self.angle += k0 * y
        self.bias += k1 * y

        p00_temp = self.p00
        p01_temp = self.p01

        self.p00 -= k0 * p00_temp
        self.p01 -= k0 * p01_temp
        self.p10 -= k1 * p00_temp
        self.p11 -= k1 * p01_temp

        return self.angle


def accel_to_angles(accel):
    ax = accel["x"]
    ay = accel["y"]
    az = accel["z"]

    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
    return roll, pitch
