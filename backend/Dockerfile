
FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY dirtbag /code/dirtbag
COPY all_crags.json /code/dirtbag

CMD ["uvicorn", "dirtbag.main:app", "--host", "0.0.0.0", "--port", "80"]