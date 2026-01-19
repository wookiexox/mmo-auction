FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml ./

RUN poetry install --no-root --no-interaction

COPY . .

CMD ["python", "-u", "worker.py"]