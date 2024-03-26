# Calmerge

A utility to merge calendar feeds together, optionally offsetting by a given number of days

Individual calendars can be protected by basic authentication if required (values can be read from environment variables, too).

## Usage

Calendars are served based on their [name](#configuration), at `/{name}.ics`.

Calendars which allow custom offsets (`allow_custom_offset = true`) can add `?offset_days=3` to customize the offset. Events can only be offset ±10 years. When not configured, this parameter is ignored.

### Static

`calmerge` also supports being used as a static content generator - whereby calendars are saved to files rather than being served by a web server.

To do this, run:

```
calmerge write ./calendars
```

Each calendar will be saved as a `.ics` file based on its name to the `./calendars` directory.

## Deployment

`calmerge` is available as a Docker container. Configuration should be mounted to `/app/calendars.toml`. An empty file is provided so the server will start successfully.

By default, `calmerge` listens on port `3000` or `$PORT`.

### Manually

You will need Python and `poetry` installed.

```
poetry install --no-dev
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
