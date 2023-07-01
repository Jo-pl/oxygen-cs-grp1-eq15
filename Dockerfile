FROM python:3.8-slim

ARG OXYGEN_TOKEN=

COPY . /usr/src/app/

# Install the app
WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
RUN pipenv install

#RUN pipenv run lint
#RUN pipenv run test

ENV OXYGEN_TOKEN=$OXYGEN_TOKEN

# Start the server when the docker image starts
CMD pipenv run start
