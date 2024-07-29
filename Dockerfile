# defualts to latest mysql version
ARG MYSQL_VERSION=latest

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

RUN . /etc/os-release; \
  if (( $VERSION_ID > 11 )); then \
  pip install \
  --break-system-packages \
  -r ./requirements.txt; \
  else \
  pip install \
  -r ./requirements.txt; \
  fi

COPY . ./

ENTRYPOINT [ "" ]
CMD bash
