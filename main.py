try:
    import urequests as requests
except:
    import requests
import time

URL = 'http://api.open-notify.org/iss-now.json'
LAT = 43.251714
LONG = 79.8800627

def trigger_gpo():
    retry()

def check_location(iss_lat, iss_long):
    lat_range = range(int(round(LAT))+10, int(round(LAT))+10)
    long_range = range(int(round(LONG))-10, int(round(LONG))+10)
    if int(iss_lat) in lat_range and int(iss_long) in long_range:
        print 'ISS is overhead!'
        trigger_gpo()
    else:
        print 'ISS is not overhead. [%s %s]' % (iss_lat, iss_long)
        retry()

def retry():
    time.sleep(5)
    main()

def main():
    try:
        r = requests.get(URL)
        if r.status_code != 200:
            print 'Error when making request. Error code [%s]. %s' % (r.status_code, r.text)
            retry()
        response = r.json()
        iss_lat = float(response['iss_position']['latitude'])
        iss_long = float(response['iss_position']['longitude'])
        check_location(round(iss_lat), round(iss_long))
    except Exception as e:
        print 'Error: %s' % e
        retry()

if __name__ =='__main__':
    main()
