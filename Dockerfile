FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
ADD pyproject.toml /app
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --only main --no-root --no-directory
COPY app/ ./app
COPY settings/ ./settings