"""
Define the root logger for the application
We use the root logger to ensure all subsequent loggers inherit the configuration.
"""

import logging
from pathlib import Path
import sys

# Define the root logger for the application
# We use the root logger to ensure all subsequent loggers inherit the configuration.
ROOT_LOGGER = logging.getLogger()


def setup_app_logging(log_file_path: Path, level=logging.INFO):
    """
    Configures the application's logging system, creating a file handler
    at the specified log_file_path.

    This function removes existing handlers to prevent duplicate messages.
    """

    # 1. Clear any existing handlers to avoid logging to the old default path
    # and prevent duplicate messages if this function is called multiple times.
    for handler in ROOT_LOGGER.handlers[:]:
        ROOT_LOGGER.removeHandler(handler)

    # 2. Set the overall minimum logging level
    ROOT_LOGGER.setLevel(level)

    # 3. Create a formatter for consistent log message structure
    formatter = logging.Formatter(
        # "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        "%(levelname)s - %(message)s"
    )

    # 4. Add a File Handler using the custom path
    try:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        ROOT_LOGGER.addHandler(file_handler)
    except IOError as e:
        # Fallback to standard error if file logging fails (e.g., permissions)
        print(f"Error setting up file logging to {log_file_path}: {e}", file=sys.stderr)

    # 5. Optionally, add a Stream Handler for console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only show warnings/errors in console
    console_handler.setFormatter(formatter)
    ROOT_LOGGER.addHandler(console_handler)


# You can keep other general utility functions here (e.g., data loading)
def load_data(file_path: str):
    ROOT_LOGGER.info(f"Loading data from: {file_path}")
    # ... implementation of data loading
    return []
