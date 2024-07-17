# Imports go at the top
from microbit import *
from machine import *

def move_forward(speed):
    i2c.write(0x10, bytearray([0, 1]))
    i2c.write(0x10, bytearray([1, speed]))
    i2c.write(0x10, bytearray([2, 1]))
    i2c.write(0x10, bytearray([3, speed]))


def move_backward(speed):
    i2c.write(0x10, bytearray([0, 2]))
    i2c.write(0x10, bytearray([1, speed]))
    i2c.write(0x10, bytearray([2, 2]))
    i2c.write(0x10, bytearray([3, speed]))


def move_stop():
    i2c.write(0x10, bytearray([0, 0]))
    i2c.write(0x10, bytearray([2, 0]))


# Init the coder
i2c.init()
p = 10

i2c.write(0x10, bytearray([4]))
tour_gauche_old = i2c.read(0x10, 2)
i2c.write(0x10, bytearray([6]))
tour_droite_old = i2c.read(0x10, 2)
tour_mean_old = (int.from_bytes(tour_gauche_old, "big") + int.from_bytes(tour_droite_old, "big"))/ 2
dist_diff_old = 0
consigne = 592
sens = 1
distance_total = 0

# Code in a 'while True:' loop repeats forever
while True:
    sleep(100)
    i2c.write(0x10, bytearray([4]))
    tour_gauche_new = i2c.read(0x10, 2)
    i2c.write(0x10, bytearray([6]))
    tour_droite_new = i2c.read(0x10, 2)
    tour_mean_new = (int.from_bytes(tour_gauche_new, "big") + int.from_bytes(tour_droite_new, "big"))/ 2
    dist_diff = (tour_mean_new - tour_mean_old) * sens
    distance_total += dist_diff
    erreur = consigne - distance_total
    if distance_total < consigne:
        sens = 1
        P_e = int(p * erreur)
        P_e = P_e if P_e <= 255 else 255
        move_forward(P_e)
    elif distance_total > consigne:
        sens = -1
        P_e = abs(int(p * erreur))
        P_e = P_e if P_e <= 255 else 255
        move_backward(P_e)
    else:
        move_stop()
    
    tour_mean_old = tour_mean_new