# Calmerge

A utility to merge calendar feeds together, optionally offsetting by a given number of days

## Features

- Merge multiple calendars into a single calendar
- Create duplicate events at a given offset (useful for showing reminders as calendar events)
- Use basic auth to protect calendars
- Use environment variables to include sensitive parameters in upstream calendar URLs or basic auth credentials
- [Static](#static) output option

## Usage

Calendars are served based on their [slug](#configuration), at `/{slug}.ics`.

Additional events cen be added at offsets from the original date using the `offset_days` configuration. Events can only be offset ±10 years.

### Static

`calmerge` also supports being used as a static content generator - whereby calendars are saved to files rather than being served by a web server.

To do this, run:

```
calmerge write ./calendars
```

Each calendar will be saved as a `.ics` file based on its slug to the `./calendars` directory.

### Listing

A listing page can be served at `/all/` using:

```toml
[listing]
enabled = true
```

Basic auth can be enabled using `auth = `.

Basic auth credentials for each calendar are not output in the listing. This can be enabled enabled using `include_credentials` on the `[listing]`.

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
slug = "python"
urls = [
    "https://endoflife.date/calendar/python.ics",
]
```

This calendar will then be exposed at `/python.ics`.

See [`tests/calendars.toml`](./tests/calendars.toml) for a more complete example.

Configuration can be validated using `calmerge validate`.
