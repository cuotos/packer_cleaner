FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY code .

CMD [ "python3", "index.py" ]