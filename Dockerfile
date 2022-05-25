FROM ubuntu:20.04
COPY . /
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install python3 python3-pip \
 && pip install plexapi \
 && pip install mysql-connector-python \
 && apt-get install -y gcc g++ libxml2-dev libxslt-dev libz-dev wget \
 && sudo apt install mysql-server \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get --purge autoremove wget gcc g++ libxml2-dev libxslt-dev libz-dev -y \
 && apt-get clean \
 && apt-get update \
 && apt-get check \
 && apt-get -f install \
 && apt-get autoclean \
 && rm -rf /requirements.txt /tmp/* /var/tmp/* /var/lib/apt/lists/*
VOLUME /config
ENTRYPOINT ["/tini", "-s", "python3", "pum.sh", "--"]
