# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install --timeout 1000 -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]