FROM python:3 AS base

WORKDIR /usr/scr/app

RUN pip install --no-cache-dir numpy

COPY . .

EXPOSE 3000

FROM base AS client

CMD [ "python", "simple_client.py" , "1.0", "--ip", "server-ip" ]

FROM base AS server

CMD [ "python", "simple_server.py" , "1.0", "--ip", "server-ip" ]

