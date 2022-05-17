FROM python:3.7-buster

ENV TZ=America/Toronto

WORKDIR /usr/src/app

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y vim-tiny less && \
    ln -s /usr/bin/vim.tiny /usr/bin/vim && \
    rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction
COPY . .
RUN chmod +x gunicorn_starter.sh

CMD ["./gunicorn_starter.sh"]
