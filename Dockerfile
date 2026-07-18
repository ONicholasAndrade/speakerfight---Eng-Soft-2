FROM python:2.7

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN sed '/fixmydjango==0.3.2/d' requirements.txt > requirements-ci.txt && \
    pip install -r requirements-ci.txt

COPY . /code/