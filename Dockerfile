FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    mariadb-server \
    python3-pip

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/activate

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8010

CMD ["/venv/bin/python", "pum.py"]
