import machine
import time
from config import TRIGGER_PIN, ECHO_PIN

class HCSR04:
    def __init__(self, trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN, echo_timeout_us=500*2*30, threshold_cm=5):
        self.trigger = machine.Pin(trigger_pin, mode=machine.Pin.OUT)
        self.echo = machine.Pin(echo_pin, mode=machine.Pin.IN)
        self.echo_timeout_us = echo_timeout_us
        self.threshold_cm = threshold_cm # Minimum change in cm to consider as a trigger
        self.last_distance = None

    def _send_pulse_and_wait(self):
        self.trigger.value(0)
        time.sleep_us(5)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110:
                raise OSError('Out of range')
            raise ex

    def distance_cm(self):
        pulse_time = self._send_pulse_and_wait()
        distance = (pulse_time / 2) / 29.1
        return distance

    def is_triggered(self):
        current_distance = self.distance_cm()
        if self.last_distance is None:
            self.last_distance = current_distance
            return False
        
        if abs(current_distance - self.last_distance) >= self.threshold_cm:
            self.last_distance = current_distance
            return True
        
        return False