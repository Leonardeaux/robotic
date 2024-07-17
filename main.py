import machine
import music
import time
import math
from microbit import *


r = 0.0215

class Robot:
    def __init__(self):
        self.motor_address = 0x10

        i2c.init()
        self.stop()

        self.P = 30000
        
        
    def forward(self, speed=150):
        i2c.write(self.motor_address, bytearray([0, 1, speed, 1, speed]))
        
    def stop(self):
        i2c.write(self.motor_address, bytearray([0, 1, 0, 1, 0]))
        i2c.write(self.motor_address, bytearray([4, 0]))
        i2c.write(self.motor_address, bytearray([6, 0]))

    def backward(self, speed=150):
        i2c.write(self.motor_address, bytearray([0, 2, speed, 2, speed]))
        
    def beep(self, freq=440, duration=100):
        music.pitch(freq, duration)
        
    def distance(self, max_dist=0.4):
        # pins: trig=2, echo=8
        pin2.write_digital(1)
        time.sleep_us(10)
        pin2.write_digital(0)
        pin8.read_digital()
        t2 = machine.time_pulse_us(pin8, 1, 23200)
        if t2>0:
            dst=340.29*(t2/(2*1000000))
        else:
            dst=max_dist
        return dst
    
    def get_pid_speed(self, target, dist):
        error = target - dist
        P_error = int(self.P * error)
        if P_error > 255:
            P_error = 255

        return abs(P_error)
    
    def get_mean_turn(self):
        i2c.write(self.motor_address, bytearray([4]))
        nb_turn_left = int.from_bytes(i2c.read(robot.motor_address, 2), "big")
        i2c.write(self.motor_address, bytearray([6]))
        nb_turn_right = int.from_bytes(i2c.read(robot.motor_address, 2), "big")
        nb_turn = (nb_turn_left + nb_turn_right) / 2

        return nb_turn
    
    def get_distance(self):
        nb_turn = self.get_mean_turn()
        dist = round(2 * math.pi * r * nb_turn * (1 / 80), 4)

        return dist
    

    def set_motor_speed(self, speed):
        i2c.write(self.motor_address, bytearray([0, 1, speed, 1, speed]))

    def forward_with_distance(self, target_distance):
        distance_old = self.get_distance()
        distance_diff = 0
        direction = 1
        total_distance = 0

        while True:
            sleep(10)
            distance = self.get_distance()
            distance_diff = (distance - distance_old) * direction
            total_distance += distance_diff

            if total_distance < target_distance:
                direction = 1
                speed = self.get_pid_speed(target_distance, total_distance)
                self.forward(speed)
            elif total_distance > target_distance:
                direction = -1
                speed = self.get_pid_speed(target_distance, total_distance)
                self.backward(speed)
            else:
                self.stop()
                break

            distance_old = distance


robot = Robot()


while True:
    sleep(100)
    if button_a.is_pressed():
        robot.forward_with_distance(1)

    if button_b.is_pressed():
        robot.beep(duration=1000)
