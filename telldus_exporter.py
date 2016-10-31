#!/usr/bin/env python 

import json
import oauth.oauth as oauth
import os
import requests
import sys
import time
import threading

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from pprint import pprint
from prometheus_client import start_http_server, Gauge, MetricsHandler

API_URL="https://api.telldus.com"

telldus_sensor_data = Gauge('telldus_sensor_data', 'Sensor data', ['id', 'name', 'location', 'metric'])


class TelldusLive:

    def __init__(self, apikeys):
        self.apikeys = apikeys

    def get(self, method, params=None):
        consumer = oauth.OAuthConsumer(self.apikeys['public_key'], self.apikeys['private_key'])

        token = oauth.OAuthToken(self.apikeys['token'], self.apikeys['token_secret'])

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                consumer, token=token, http_method='GET', http_url=API_URL + "/json/" + method, parameters=params)
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
        headers = oauth_request.to_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        #conn = httplib.HTTPConnection("api.telldus.com:80")
        #conn.request('GET', "/json/" + method + "?" + urllib.urlencode(params, True).replace('+', '%20'), headers=headers)
        #response = conn.getresponse()

        response = requests.get('%s/json/%s' % (API_URL, method), headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(response.text)

        return json.loads(response.text)


# Override the metrics handler in prometheus-client with our own.
class TelldusMetricsHandler(MetricsHandler):

    def do_GET(self):
        epoch_time = int(time.time())

        for sensor in telldus.get('sensors/list')['sensor']:
            sensordata = telldus.get('sensor/info', params = { 'id': sensor['id'] })

            for data in sensordata['data']:
                telldus_sensor_data.labels(sensor['id'],
                                           sensor['name'],
                                           sensor['clientName'],
                                           data['name']).set(data['value'])

        MetricsHandler.do_GET(self)


with open('apikeys.json') as f:
    apikeys = json.load(f)
telldus = TelldusLive(apikeys)

def start_http_server(port, addr=''):
    """Starts a HTTP server for prometheus metrics as a daemon thread."""
    class TelldusPrometheusMetricsServer(threading.Thread):
        def run(self):
            httpd = HTTPServer((addr, port), TelldusMetricsHandler)
            httpd.serve_forever()
    t = TelldusPrometheusMetricsServer()
    t.daemon = True
    t.start()


def main(argv):
    start_http_server(9191)

    while True:
        time.sleep(60)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

