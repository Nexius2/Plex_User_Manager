FROM ubuntu:20.04
COPY . /
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y gcc g++ libxml2-dev libxslt-dev libz-dev python3 python3-pip mysql-server wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get --purge autoremove wget gcc g++ libxml2-dev libxslt-dev libz-dev -y \
 && apt-get clean \
 && apt-get update \
 && apt-get check \
 && apt-get -f install \
 && apt-get autoclean \
 && rm -rf /requirements.txt /tmp/* /var/tmp/* /var/lib/apt/lists/*
ENTRYPOINT ["python3"]
# run script 
CMD ["/bin/bash", "pum.sh"]
