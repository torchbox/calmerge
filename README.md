# Calmerge

A utility to merge calendar feeds together, optionally offsetting by a given number of days

Individual calendars can be protected by basic authentication if required (values can be read from environment variables, too).

## Deployment

`calmerge` is available as a Docker container. Configuration should be mounted to `/app/calendars.toml`. An empty file is provided so the server will start successfully.

By default, `calmerge` listens on port `3000` or `$PORT`.

### Manually

You will need Python and `poetry` installed.

```
poetry install
poetry run calmerge serve
```

## Configuration

Configuration is done using a TOML file. By default, this file should be `calendars.toml` in the current working directory, but this can be configured using `--config`

Example configuration:

```toml
[[calendar]]
name = "python"
urls = [
    "https://endoflife.date/calendar/python.ics",
]
```

This calendar will then be exposed at `/python.ics`.

See [`tests/calendars.toml`](./tests/calendars.toml) for a more complete example.

Configuration can be validated using `calmerge validate`.
