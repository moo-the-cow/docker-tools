FROM python:3.11-alpine
RUN mkdir /data
COPY ip_monitor.py /app/ip_monitor.py
WORKDIR /app
CMD ["python", "-u", "ip_monitor.py"]
