FROM python:3.8

# Create the virtual environment
RUN python3 -m venv /venv

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/activate

RUN echo "**** install system packages ****" \
 && apt-get install -y python3-pip python3-tk mysql-server tzdata wget \
 && wget https://raw.githubusercontent.com/blacktwin/JBOPS/master/utility/plex_api_share.py \

# Install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Run the application
CMD ["/venv/bin/python", "pum.py"]
