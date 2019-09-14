import urequests as requests


class HTTPClient(object):
    def __init__(self):
        self.url = None
        self.data = None
        self.request = None

    def post(self, url, data):
        self.url = url
        self.data = data
        payload = self._build_payload()
        self.request = requests.post(url, json=payload)

    def _build_payload(self):
        data_type = 'info'
        description = 'iss location'
        data = self.data
        return {
            "type": data_type,
            "description": description,
            "data": data
        }

    def print_response(self):
        print('POST data: %s' % self.request.text)
