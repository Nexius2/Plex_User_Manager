FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    mariadb-server \
    python3-pip

RUN python3 -m venv /venv
RUN ls -la /venv
ENV PATH="/venv/bin:$PATH"
RUN echo $PATH
RUN chmod +x /venv/bin/activate
RUN /venv/bin/python3 -m pip install --upgrade pi

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8010

ENV MYSQL_ROOT_PASSWORD=<PUM-USER>

# Create a new database and user
RUN service mysql start \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS <pum>;" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '<pumuser>'@'%' IDENTIFIED BY '<PUM-USER>';" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON <pum>.* TO '<pumuser>'@'%';" \
    && mysql -u root -p$MYSQL_ROOT_PASSWORD -e "FLUSH PRIVILEGES;"

CMD ["/venv/bin/python", "pum.py"]
