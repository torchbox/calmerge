import argparse
from . import get_aiohttp_app
from aiohttp.web import run_app
import os


def serve(args: argparse.Namespace):
    run_app(get_aiohttp_app(), port=int(os.environ.get("PORT", args.port)))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calmerge")

    subparsers = parser.add_subparsers(title="sub-commands")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.set_defaults(func=serve)
    serve_parser.add_argument("--port", type=int, default=3000)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" in args:
        exit(args.func(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
