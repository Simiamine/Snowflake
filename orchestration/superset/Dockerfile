FROM apache/superset:latest

USER root

# Installation du certificat Sanofi directement dans l'image
COPY sanofi-bundle.crt /usr/local/share/ca-certificates/sanofi-bundle.crt
RUN update-ca-certificates

# Installation des requirements de base
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Installation automatique des drivers Snowflake dans le venv
RUN /app/.venv/bin/python -m ensurepip --upgrade && \
    /app/.venv/bin/python -m pip install --upgrade pip && \
    /app/.venv/bin/python -m pip install --no-cache-dir \
        "snowflake-connector-python==3.*" \
        "snowflake-sqlalchemy==1.*" \
        --trusted-host pypi.org \
        --trusted-host pypi.python.org \
        --trusted-host files.pythonhosted.org

# Configuration du certificat pour les connexions Python
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

RUN mkdir -p /app/pythonpath
COPY superset_config.py /app/pythonpath/superset_config.py
ENV PYTHONPATH=/app/pythonpath

USER superset
