# defualts to latest mysql version
ARG MYSQL_VERSION=latest
ARG PYTHON_VERSION=3.12.5

FROM bitnami/mysql:${MYSQL_VERSION}

ARG PYTHON_VERSION

USER root

RUN apt-get update && \
  apt-get install -y \
  vim \
  curl \
  jq \
  build-essential \
  zlib1g-dev \
  libncurses5-dev \
  libgdbm-dev \
  libnss3-dev \
  libssl-dev \
  libreadline-dev \
  libffi-dev \
  libsqlite3-dev

WORKDIR /tmp/python-build

RUN curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
RUN tar vxf Python-${PYTHON_VERSION}.tgz && \
  cd Python-3.12.5 && \
  ./configure --enable-optimizations && \
  make -j $(nproc) && \
  make altinstall && \
  ln -s /usr/local/bin/python3.12 /usr/local/bin/python && \
  ln -s /usr/local/bin/python3.12 /usr/local/bin/python3 \
  ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip && \
  ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip3

WORKDIR /opt/mysql_idb

RUN rm -rf /tmp/python-build

COPY requirements.txt ./

RUN pip install -r ./requirements.txt

COPY . ./

ENTRYPOINT [ "" ]
CMD bash
