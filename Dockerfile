FROM python:3.7

WORKDIR /usr/src/app/

COPY ./Requirements.txt ./Requirements.txt

RUN pip install -r Requirements.txt
COPY . /usr/src/app/

RUN python manage.py makemigrations