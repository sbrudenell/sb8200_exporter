FROM python:3-slim

COPY . /src

RUN pip install --upgrade --default-timeout=100 --no-cache-dir /src && \
    pip install --upgrade certifi && \
    cp /usr/local/bin/sb8200_exporter /sb8200_exporter
    
EXPOSE 9195

ENTRYPOINT ["/sb8200_exporter"]
