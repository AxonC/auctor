FROM python:3.7-slim

WORKDIR /home/srv

COPY ./requirements.txt ./

RUN apt-get update && apt-get install -y libpq5 && apt-get clean

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY *.py ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
