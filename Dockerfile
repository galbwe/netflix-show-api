FROM python:3.7-buster

WORKDIR /app

COPY requirements.prod.txt ./
RUN pip install --no-cache-dir -r ./requirements.prod.txt
COPY setup.py ./
COPY netflix_show_api ./netflix_show_api
RUN pip install -e .

CMD ["uvicorn", "netflix_show_api.api:app", "--host", "0.0.0.0", "--port", "80"]