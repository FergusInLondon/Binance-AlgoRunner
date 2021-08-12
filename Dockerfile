FROM python:3.9-slim

RUN apt-get update && apt-get install build-essential -y

WORKDIR /algorunner
COPY poetry.lock pyproject.toml Makefile setup.sh /algorunner/

RUN make env-check

# @todo --no-dev --no-ansi
RUN poetry config virtualenvs.create false && make deps 

COPY . /code
ENTRYPOINT [ "make" "run" ]

# @todo - secondary layer with development dependencies removed
