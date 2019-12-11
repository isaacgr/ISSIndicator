from client import HTTPClient
import urequests as requests
import time
import machine
import network
import math

SSID = 'VIRGIN559'
PASSWORD = '412C7934'
LAT = 43.2517304
LONG = -79.8800351
OFFSET = 1000  # offset in meters from location to trigger
POLL_PERIOD = 5


class AlreadyConnectedError(Exception):
    pass


class ISSIndicator(object):
    def __init__(self, lat, long):
        self.URL = 'http://api.open-notify.org/iss-now.json'
        self.servo = None
        self.wlan = None
        self.wifi_led = None
        self.poll_led = None
	self.client = None

    def connect(self):
        if not self.wlan.isconnected():
            self.wifi_led.off()
            print('Connecting...')
            self.wlan.connect(SSID, PASSWORD)
            while not self.wlan.isconnected():
                pass
	else:
	    raise AlreadyConnectedError('Network already established')

        print('Network established')
        self.wifi_led.on()

    def initialize(self):
	# initialize wlan connection
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
	# initialize http client class
	self.client = HTTPClient()
        # Indicate wifi connection
        self.wifi_led = machine.Pin(4, machine.Pin.OUT, value=0)
        # Indicate esp is able to poll for data
        self.poll_led = machine.Pin(14, machine.Pin.OUT, value=0)
        servo_pin = machine.Pin(12)
        self.servo = machine.PWM(servo_pin, freq=50, duty=50)

    def get_coordinates(self):
        r = requests.get(self.URL)
        if r.status_code != 200:
            raise Exception('Unable to make request. Code [%s]. %s' % (
                r.status_code, r.text))
        self.poll_led.on()
        response = r.json()
        iss_lat = float(response['iss_position']['latitude'])
        iss_long = float(response['iss_position']['longitude'])
        return [iss_lat, iss_long]

    def calc_offset_degrees(self, offset):
        """
        We can use a predictor to determine if the iss is overhead.
        However this would likely vary depending on api and would force
        us to rely on that specific site.
        Calculate offset in degrees, based on offset in meters.
        """
        # radius of the earth
        R = 6378137.0
        offset = float(offset)
        # offset in radians
        dlat = offset/R
        dlong = offset/(R*math.cos(math.pi*LAT/180.0))

        lat_offset = dlat * 180.0/math.pi
        long_offset = dlong * 180.0/math.pi
        return [lat_offset, long_offset]

    def check_location(self, iss_lat, iss_long, lat_offset=0, long_offset=0):
        if iss_lat >= LAT-lat_offset and iss_lat <= LAT+lat_offset:
            lat_in_range = True
        else:
            lat_in_range = False
        if iss_long >= LONG-long_offset and iss_long <= LONG+long_offset:
            long_in_range = True
        else:
            long_in_range = False

        if lat_in_range and long_in_range:
            print('ISS is overhead! [%s %s]' % (iss_lat, iss_long))
            self.move_servo(True)
        else:
            print('ISS is not overhead. [%s %s]' % (iss_lat, iss_long))
            self.move_servo(False)

    def move_servo(self, status):
        if status == True:
            self.servo.duty(98)
        else:
            self.servo.duty(50)

    def post_data(self, *args):
        url = 'http://irowell-temperature.herokuapp.com/api/data'
        iss_lat, iss_long = args
        data = {
	    "latitude": iss_lat,
	    "longitude": iss_long
	}
	self.client.post(url, data)
	self.client.print_response()


def main():
    iss = ISSIndicator(LAT, LONG)
    iss.initialize()
    lat_offset, long_offset = iss.calc_offset_degrees(OFFSET)
    while True:
        iss.poll_led.off()
        try:
            iss.connect()
	except AlreadyConnectedError:
	    pass
        time.sleep(POLL_PERIOD)
        try:
            iss_lat, iss_long = iss.get_coordinates()
            iss.post_data(iss_lat, iss_long)
            iss.check_location(iss_lat, iss_long, lat_offset, long_offset)
        except Exception as e:
            print('Error: %s' % e)


main()
