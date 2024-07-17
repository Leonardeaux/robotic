import machine
import time
import math
from microbit import *


def ultrasonic(maxDist=0.4):
    # pins: trig=2, echo=8
    pin2.write_digital(1)
    time.sleep_us(10)
    pin2.write_digital(0)
    pin8.read_digital()
    timeOut = int(maxDist * 2000000 / 340.29)
    t2 = machine.time_pulse_us(pin8, 1, timeOut)
    time.sleep(1)
    if t2 > 0:
        dst = 340.29 * (t2 / (2 * 1000000))
    else:
        dst = maxDist
    return dst


def set_motor_speed(speed, direction):
    i2c.write(0x10, bytearray([0, direction, speed, direction, speed]))


def set_motor_spin(speed, spin):
    if spin == 1:
        i2c.write(0x10, bytearray([0, 1, speed, 2, speed]))
    elif spin == 2:
        i2c.write(0x10, bytearray([0, 2, speed, 1, speed]))
    else:
        i2c.write(0x10, bytearray([0, 0, 0, 0, 0]))


def update_codeur_spin(spin_real, spin_old_total, direction):
    i2c.write(0x10, bytearray([4]))
    nb_turn_left = int.from_bytes(i2c.read(0x10, 2), "big")
    i2c.write(0x10, bytearray([6]))
    nb_turn_right = int.from_bytes(i2c.read(0x10, 2), "big")
    nb_turn_left = nb_turn_left * (1 / 80) * 2 * math.pi
    nb_turn_right = nb_turn_right * (1 / 80) * 2 * math.pi
    if direction == 1:
        nb_turn_right = nb_turn_right * -1
    else:
        nb_turn_left = nb_turn_left * -1
    spin_total = spin_old_total + r * (
                ((nb_turn_left % (2 * math.pi)) - 2 * (nb_turn_right * 2 * math.pi)) / (l))  # (2 * l)
    print("Angle Spin Gauche", (nb_turn_left * 2 * math.pi) % (2 * math.pi))
    print("Angle Spin Droit", (nb_turn_right * 2 * math.pi) % (2 * math.pi))

    if spin == 2:
        spin_real -= spin_total - spin_old_total
    else:
        spin_real += spin_total - spin_old_total
    return spin_real, spin_total


def update_codeur_speed(dist_real, dist_old_total):
    i2c.write(0x10, bytearray([4]))
    nb_turn_left = int.from_bytes(i2c.read(0x10, 2), "big")
    i2c.write(0x10, bytearray([6]))
    nb_turn_right = int.from_bytes(i2c.read(0x10, 2), "big")
    nb_turn = (nb_turn_left + nb_turn_right) / 2
    print("Nbr Turn Left", nb_turn_left)
    print("Nbr Turn Right", nb_turn_right)
    dist_total = round(2 * math.pi * r * nb_turn * (1 / 80), 4)
    if direction == 2:
        dist_real -= dist_total - dist_old_total
    else:
        dist_real += dist_total - dist_old_total
    return dist_real, dist_total


def PID_spin(target_spin, spn, spin):
    error = target_spin - spn
    if spin == 1:
        P_error = P_spin * error
    else:
        P_error = P_spin * error * -1
    if P_error > 255:
        P_error = 255
    return P_error


def PID_speed(target_dist, dist, direction):
    error = target_dist - dist
    if direction == 1:
        P_error = P * error
    else:
        P_error = P * error * -1
    if P_error > 255:
        P_error = 255
    return P_error


i2c.init()
r = 0.0215  # Constante rayon de la roue
l = 0.1  # Distance entre les roues
P = 3000  # 3000 # Constante à tester
P_spin = 1.2  # Constante à tester
i2c.write(0x10, bytearray([0, 1, 0, 1, 0]))
i2c.write(0x10, bytearray([4, 0]))
i2c.write(0x10, bytearray([6, 0]))
dist_old_total = 0
spin_old_total = 0
direction = 1
spin = 1
target_dist = 1
target_spin = 90
dist_real = 0
spin_real = 0
to_not_break = True
while to_not_break:
    if button_a.is_pressed() and button_b.is_pressed():
        value = round(ultrasonic(10), 2)
        display.show(value)
        # print(value)
        display.show(Image.SQUARE)
    elif button_a.is_pressed():
        sleep(2000)
        while True:
            sleep(10)
            spin_real, spin_old_total = update_codeur_spin(spin_real, spin_old_total, direction)
            print(spin_real, spin_old_total)
            if spin_real < target_spin:
                spin = 1
            elif spin_real > target_spin:
                spin = 2
            v_rotor = int(PID_spin(target_spin, spin_real, spin))
            print(v_rotor)
            set_motor_spin(v_rotor, spin)
            if button_b.is_pressed():
                i2c.write(0x10, bytearray([0, 1, 0, 1, 0]))
                i2c.write(0x10, bytearray([4, 0]))
                i2c.write(0x10, bytearray([6, 0]))
                sleep(2000)
                break
    elif button_b.is_pressed():
        sleep(2000)
        while True:
            sleep(10)
            dist_real, dist_old_total = update_codeur_speed(dist_real, dist_old_total)
            print(dist_real, dist_real)
            if dist_real < target_dist:
                direction = 1
            elif dist_real > target_dist:
                direction = 2
            v_motor = int(PID_speed(target_dist, dist_real, direction))
            print(v_motor)
            set_motor_speed(v_motor, direction)
            if button_b.is_pressed():
                i2c.write(0x10, bytearray([0, 1, 0, 1, 0]))
                i2c.write(0x10, bytearray([4, 0]))
                i2c.write(0x10, bytearray([6, 0]))
                sleep(2000)
                break
    else:
        pass
    sleep(250)
