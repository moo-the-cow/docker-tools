FROM python:3.11-alpine

# Set up directories and pre-create the genuine tracking file
RUN mkdir -p /data /app && echo "{}" > /data/last_ip.json

WORKDIR /app

# Copy only the Python application script
COPY ip_monitor.py /app/ip_monitor.py

# Launch Python directly
CMD ["python", "-u", "/app/ip_monitor.py"]
