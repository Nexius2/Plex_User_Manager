FROM python:3

WORKDIR /usr/src

COPY . .

RUN echo "**** install system packages ****" \

 && apt-get install -y python3-tk mysql-server tzdata wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 
CMD ["python", "./pum.py"]
