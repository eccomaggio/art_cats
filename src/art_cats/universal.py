"""
Order form for TAY / ART libraries to replace excel-based form.
Contact: Ross Jones, Osney One
"""

# import logging
from . import log_setup
from . import logic

from enum import Enum
from pathlib import Path
from .settings import Default_settings
from . import form_gui


def main():
    class COL(Enum):
        ## need pto be in same order as CSV / excel fields
        @staticmethod
        def _generate_next_value_(count):
            return count

        def __new__(cls, display_title: str):
            member = object.__new__(cls)
            member._value_ = cls._generate_next_value_(len(cls.__members__))
            member.display_title = display_title
            return member

        def __init__(self, title: str):
            self.display_title = title

    ##### Tailor settings

    settings = Default_settings()
    settings.known_types = logic.known_patterns
    headers = []

    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    CUSTOM_LOG_FILE = settings.files.full_output_dir / "logger.log"

    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
    form_gui.run(settings, headers, COL)


if __name__ == "__main__":
    main()
