import RPi.GPIO as GPIO

PIN = 26
GPIO.setmode(GPIO.BCM)


def callback():
    print("button")

GPIO.setup(PIN,GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(PIN,GPIO.FALLING, callback = callback,bouncetime = 100)


try:
    while True:
        pass
finally:
    GPIO.cleanup()
