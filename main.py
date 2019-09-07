try:
    import urequests as requests
except:
    import requests
import time
import machine


class ISSIndicator(object):
    def __init__(self):
        self.URL = 'http://api.open-notify.org/iss-now.json'
        self.LAT = 43.251714
        self.LONG = 79.8800627
        self.servo_pin = None
        self.servo = None

    def init_servo(self):
        self.servo_pin = machine.Pin(12)
        self.servo = machine.PWM(self.servo_pin, freq=50, duty=77)

    def get_coordinates(self):
        r = requests.get(self.URL)
        if r.status_code != 200:
            print 'Error when making request. Error code [%s]. %s' % (r.status_code, r.text)
            retry()
        response = r.json()
        iss_lat = float(response['iss_position']['latitude'])
        iss_long = float(response['iss_position']['longitude'])
        return [iss_lat, iss_long]

    def check_location(self, iss_lat, iss_long):
        lat_range = range(int(round(self.LAT))-10, int(round(self.LAT))+10)
        long_range = range(int(round(self.LONG))-10, int(round(self.LONG))+10)
        if int(iss_lat) in lat_range and int(iss_long) in long_range:
            print 'ISS is overhead!'
            self.move_servo(True)
        else:
            print 'ISS is not overhead. [%s %s]' % (iss_lat, iss_long)
            self.move_servo(False)

    def move_servo(self, status):
        if status == True:
            self.servo.duty(102)
        else:
            self.servo.duty(77)


def main():
    iss = ISSIndicator()
    iss.init_servo()
    while True:
        try:
            iss_lat, iss_long = iss.get_coordinates()
            iss.check_location(round(iss_lat), round(iss_long))
        except Exception as e:
            print 'Error: %s' % e


if __name__ == '__main__':
    main()
