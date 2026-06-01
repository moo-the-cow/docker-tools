FROM python:3.11-alpine

RUN mkdir -p /data /app
WORKDIR /app

# Copy the application source files
COPY entrypoint.sh /app/entrypoint.sh
COPY ip_monitor.py /app/ip_monitor.py

# Ensure the entrypoint has execution permissions
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
