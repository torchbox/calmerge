import argparse
import os
from pathlib import Path

from aiohttp.web import run_app
from pydantic import ValidationError

from . import get_aiohttp_app
from .config import Config
from .static import write_calendar


def file_path(path: str) -> Path:
    path_obj = Path(path).resolve()

    if not path_obj.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {path}")

    return path_obj


def serve(args: argparse.Namespace) -> None:
    config = Config.from_file(args.config)
    print(f"Found {len(config.calendars)} calendar(s)")
    run_app(get_aiohttp_app(config), port=int(os.environ.get("PORT", args.port)))


def validate_config(args: argparse.Namespace) -> None:
    try:
        Config.from_file(args.config)
    except ValidationError as e:
        print(e)
        exit(1)
    else:
        print("Config is valid!")

    return None


def write_calendars(args: argparse.Namespace) -> None:
    output_dir: Path = args.out_dir.resolve()

    output_dir.mkdir(exist_ok=True, parents=True)

    config = Config.from_file(args.config)

    for calendar_config in config.calendars:
        output_file = output_dir / f"{calendar_config.name}.ics"
        print("Saving", output_file)
        write_calendar(calendar_config, output_file)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calmerge")

    parser.add_argument("--config", type=file_path, default="calendars.toml")

    subparsers = parser.add_subparsers(title="sub-commands")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.set_defaults(func=serve)
    serve_parser.add_argument("--port", type=int, default=3000)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.set_defaults(func=validate_config)

    write_parser = subparsers.add_parser("write")
    write_parser.add_argument("out_dir", type=Path)
    write_parser.set_defaults(func=write_calendars)

    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    if "func" in args:
        exit(args.func(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
