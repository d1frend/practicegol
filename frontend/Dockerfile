FROM python:3.11

RUN mkdir /docker_front

WORKDIR /docker_front

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn frontend:app2 --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

