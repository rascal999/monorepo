FROM grafana/grafana-enterprise:latest

USER root

# Install Python and required packages
RUN apk add --no-cache python3 py3-pip

# Create a virtual environment and install packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install flask pymongo

# Copy our MongoDB API script
COPY mongodb_api.py /usr/local/bin/
RUN chmod +x /usr/local/bin/mongodb_api.py

# Create a startup script
COPY start.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start.sh

# Switch back to grafana user
USER grafana

ENTRYPOINT ["/usr/local/bin/start.sh"]