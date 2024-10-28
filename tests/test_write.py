import subprocess
import sys
from pathlib import Path

import icalendar

from calmerge.config import Config


def test_write_config(tmp_path: Path, config: Config, config_path: Path) -> None:
    subprocess.check_output(
        [
            sys.executable,
            "-m",
            "calmerge",
            "--config",
            str(config_path),
            "write",
            str(tmp_path),
        ]
    )
    assert len(list(tmp_path.glob("*.ics"))) == len(config.calendars)

    for calendar_config in config.calendars:
        calendar_path = tmp_path.joinpath(f"{calendar_config.slug}.ics")
        assert calendar_path.is_file()

        calendar = icalendar.Calendar.from_ical(calendar_path.read_text())
        assert calendar.errors == []
