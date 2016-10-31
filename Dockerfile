FROM python:2.7
COPY telldus_exporter.py.py /usr/src/app
CMD ['python', '/usr/src/app/telldus_exporter.py' ]
