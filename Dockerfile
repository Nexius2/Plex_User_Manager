FROM python:3

RUN apt-get update -y

ENV CONFIG_PATH=./.config/plexapi/config.ini

RUN  apt-get install -y python3-pip python3-tk mysql-server tzdata wget 
RUN  wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py 
RUN  pip install requests PlexAPI urllib3 mysql-connector-python

CMD ["./pum.py"]
ENTRYPOINT ["python3"]
