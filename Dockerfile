FROM python:3.13.0

WORKDIR /app

COPY ./src /app/src
COPY requirements.txt /app/requirements.txt
COPY run.py /app/run.py
COPY .env /app/.env


RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["run.py"]