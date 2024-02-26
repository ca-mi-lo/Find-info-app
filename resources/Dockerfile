FROM python:3.11.8-slim-bookworm

ENV POETRY_VERSION=1.7.1
ARG UID=1000
ARG GID=1000

RUN pip install poetry

WORKDIR /app
RUN groupadd -g ${GID} streamlit 
RUN useradd -u ${UID} -g ${GID} -d /app streamlit
RUN chown -R ${UID}:${GID} /app
USER streamlit

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-root --with elasticsearch --without dev

COPY . .
RUN poetry install --no-dev

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stscore/health
ENTRYPOINT [ "poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0" ]
