FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    mariadb-server \
    python3-pip \
	wget

RUN python3 -m venv /venv
RUN ls -la /venv
ENV PATH="/venv/bin:$PATH"
RUN echo $PATH
RUN chmod +x /venv/bin/activate
RUN /venv/bin/python3 -m pip install --upgrade pip
# RUN wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8010

ENV MYSQL_ROOT_PASSWORD=PUM-USER

RUN service mariadb status | grep -q 'Active: active (running)' || service mariadb start
RUN service mariadb status

# Create a new database and user
RUN service mysql start \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE SCHEMA IF NOT EXISTS pum DEFAULT CHARACTER SET utf8;" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER IF NOT EXISTS 'pumuser'@'%' IDENTIFIED BY 'PUM-USER';" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON pum.* TO 'pumuser'@'%';" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "FLUSH PRIVILEGES;"

CMD ["/venv/bin/python", "pum.py"]
