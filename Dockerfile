FROM ubuntu:latest
LABEL maintainer="Nexius2" \
      name="plex_user_manager" \
      version="0.47"
WORKDIR /usr/app
COPY pum.py ./

ENV TZ=Europe/Paris
ENV CONFIG_PATH=./.config/plexapi/config.ini
ARG DEBIAN_FRONTEND=noninteractive
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y python3 python3-pip python3-tk mysql-server tzdata wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get clean \
CMD ["python3", "./pum.py"]
