FROM python:3.10-alpine

WORKDIR /app
RUN addgroup -S app && adduser -S app app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app
RUN apk add -U --no-cache build-base && \
 pip install -r /app/requirements.txt && \
 apk del build-base

COPY ./src /app
USER app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
