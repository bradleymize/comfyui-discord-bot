FROM python:3.13.0

WORKDIR /app

COPY ./src /app/src
COPY requirements.txt /app/requirements.txt
COPY run.py /app/run.py

RUN pip install -r requirements.txt && \
    rm -rf /app/src/models && \
    rm -rf /app/src/workflows

ENTRYPOINT ["python"]
CMD ["run.py"]