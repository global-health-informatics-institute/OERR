import RPi.GPIO as GPIO


class led_control:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)

    def turn_led_off(self):
        GPIO.output(20, GPIO.LOW)

    def turn_led_on(self):
        GPIO.output(20, GPIO.HIGH)

    def charger_led_green(self):
        GPIO.output(27, GPIO.LOW)

    def charger_led_red(self):
        GPIO.output(27, GPIO.HIGH)

    def charger_led_off(self):
        GPIO.output(27, GPIO.LOW)
