FROM python:3
COPY . /
ENV CONFIG_PATH=./.config/plexapi/config.ini
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y python3 python3-pip python3-tk mysql-server tzdata wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get clean \
CMD ["python", "./pum.py"]

