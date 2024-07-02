# defualts to latest mysql 8
ARG MYSQL_VERSION=8

FROM bitnami/mysql:${MYSQL_VERSION}

USER root

RUN apt-get update && \
  apt-get install -y \
  python3 \
  python3-pip \
  python-is-python3 \
  vim

WORKDIR /opt/mysql_idb
COPY requirements.txt ./

RUN pip install \
  --break-system-packages \
  -r ./requirements.txt

COPY . ./

ENTRYPOINT [ "" ]
CMD bash
