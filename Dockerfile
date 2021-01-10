FROM python:3.9-slim-buster

WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/logs
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD [ "python", "run.py" ]

# docker build -t kasa_controller .
# docker run -p 5000:5000 --detach --name kasa_controller kasa_controller