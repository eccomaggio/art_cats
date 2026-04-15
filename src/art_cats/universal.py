"""
Order form for TAY / ART libraries to replace excel-based form.
Contact: Ross Jones, Osney One
"""

from . import log_setup
from . import logic

from enum import Enum
from pathlib import Path
from .settings import Default_settings
from . import form_gui


def main():
    settings = Default_settings()
    settings.known_patterns = logic.known_patterns
    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    CUSTOM_LOG_FILE = settings.files.full_output_dir / "logger.log"
    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)

    form_gui.run(settings)


if __name__ == "__main__":
    main()
