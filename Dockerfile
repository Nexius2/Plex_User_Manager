FROM ubuntu:latest
LABEL maintainer="Nexius2" \
      name="plex_user_manager" \
      version="0.2"
COPY . /
ENV TZ=Europe/Paris
ENV CONFIG_PATH=./.config/plexapi/config.ini
ARG DEBIAN_FRONTEND=noninteractive
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y python3 python3-pip python3-tk mysql-server tzdata wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \
 # && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py -P ./api/ \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 # && rm -rf /requirements.txt /tmp/* /var/tmp/* /var/lib/apt/lists/*
ENTRYPOINT ["python3"]
# run script 
CMD ["./pum_web.py"]