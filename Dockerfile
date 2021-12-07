FROM python:3.10

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY aregalo-backend /aregalo-backend

WORKDIR /aregalo-backend

EXPOSE 8757

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8757"]