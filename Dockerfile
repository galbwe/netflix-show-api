FROM python:3.7-buster

WORKDIR /app

COPY requirements.prod.txt ./
COPY logging.config.yaml ./
RUN pip install --no-cache-dir -r ./requirements.prod.txt
COPY setup.py ./
COPY netflix_show_api ./netflix_show_api
RUN pip install .

CMD ["uvicorn", "netflix_show_api.api:app", "--host", "0.0.0.0", "--port", "80"]