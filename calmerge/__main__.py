import argparse
import os
from pathlib import Path

from aiohttp.web import run_app
from pydantic import ValidationError

from . import get_aiohttp_app
from .config import Config


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


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calmerge")

    parser.add_argument("--config", type=file_path, default="calendars.toml")

    subparsers = parser.add_subparsers(title="sub-commands")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.set_defaults(func=serve)
    serve_parser.add_argument("--port", type=int, default=3000)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.set_defaults(func=validate_config)

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
