FROM python:3.11

RUN mkdir /docker_backend

WORKDIR /docker_backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:5252




