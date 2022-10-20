FROM ubuntu:latest
LABEL maintainer="Nexius2" \
      name="plex_user_manager" \
      version="0.47"
WORKDIR /usr/app
COPY pum.py ./

ENV TZ=Europe/Paris
ENV CONFIG_PATH=./.config/plexapi/config.ini
ARG DEBIAN_FRONTEND=noninteractive
RUN echo "**** install system packages ****" 
RUN  apt-get update 
RUN  apt-get upgrade -y --no-install-recommends 
RUN  apt-get install -y python3 python3-pip python3-tk mysql-server tzdata wget 
RUN  wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py 
RUN  pip install --no-cache-dir --upgrade --requirement /requirements.txt 
RUN  apt-get clean 
CMD ["python3", "./pum.py"]
