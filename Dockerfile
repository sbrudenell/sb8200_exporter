FROM python:3-slim

COPY . /src

RUN pip install --upgrade /src && \
    cp /usr/local/bin/sb8200_exporter /sb8200_exporter

EXPOSE 9195

ENTRYPOINT ["/sb8200_exporter"]
