# telldus-exporter
A simple [Prometheus](http://prometheus.io) exporter of [Telldus](http://telldus.com) sensor data.

## Instructions
Add your Telldus Live API key and token to apikeys.json before launching the script or building the Dockerfile.

## Docker
The included Dockerfile will build a docker image with your apikeys.json included. Build it and start it with:

```sh
docker build -t <youruser>/telldus-exporter .
docker run -d -p 9191:9191 --restart="always" <youruser>/telldus-exporter:latest
```

Point your web browser to http://<yourserver>:9191/metrics to verify you get data from the Telldus API.
