FROM python:3.8-slim-buster

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD [ "python", "app.py" ]

# docker build -t kasa_controller .
# docker run -p 5000:5000 --detach --name kasa_controller kasa_controller