FROM python:3.11
WORKDIR /app
RUN apt update -y && apt upgrade -y
RUN apt install gcc -y
RUN apt install python3-dev -y
RUN apt install openssl -y
RUN pip install --upgrade pip --no-cache-dir
COPY . /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
EXPOSE 80
CMD gunicorn -b 0.0.0.0:80 -w=4 --log-level=debug application:app