FROM python:3.11-slim

ENV VIRTUAL_ENV=/venv

RUN useradd calmerge --create-home && mkdir /app $VIRTUAL_ENV && chown -R calmerge /app $VIRTUAL_ENV

WORKDIR /app

# Install poetry at the system level
RUN pip install --no-cache poetry==1.8.2

USER calmerge

RUN python -m venv $VIRTUAL_ENV

ENV PATH=$VIRTUAL_ENV/bin:$PATH

COPY --chown=calmerge pyproject.toml poetry.lock ./

RUN pip install --no-cache --upgrade pip && poetry install --no-dev --no-root && rm -rf $HOME/.cache

COPY --chown=calmerge . .

# Run poetry install again to install our project
RUN poetry install --no-dev

RUN python -m compileall -q $VIRTUAL_ENV .

RUN touch /app/calendars.toml

EXPOSE 3000

CMD ["/venv/bin/calmerge", "serve"]
