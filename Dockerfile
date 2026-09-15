FROM python:3.13-slim

ENV VIRTUAL_ENV=/venv

RUN useradd calmerge --create-home && mkdir /app $VIRTUAL_ENV && chown -R calmerge /app $VIRTUAL_ENV

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

USER calmerge

RUN uv venv $VIRTUAL_ENV

ENV PATH=$VIRTUAL_ENV/bin:$PATH

COPY --chown=calmerge pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-local --no-cache --active

COPY --chown=calmerge . .

# Run uv install again to install our project
RUN uv sync --frozen --no-cache --active

RUN touch /app/calendars.toml

EXPOSE 3000

CMD ["/venv/bin/calmerge", "serve"]
