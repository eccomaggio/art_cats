"""
Handles generic input/output file writes
does NOT handle specific marc_21 marc files or excel io
(These are currently still within marc_21.py)
"""

import yaml
from pathlib import Path
import csv
import logging

logger = logging.getLogger(__name__)

def save_as_yaml(file: str, data) -> None:
    with open(file, mode="wt", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)


# def open_yaml_file(file:str):
def open_yaml_file(file_path: Path):
    # with open(file, mode="rt", encoding="utf-8") as f:
    # file_path = settings.files.app_dir / Path(file)
    # file_path = Path(file)
    with open(file_path, mode="rt", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_plaintext_from_file(file_name: str) -> str:
    """Reads the plaintext content of the specified file, returning a default message on error. The plaintext could also encode markdown or html (as is the case here)."""
    path = Path(file_name)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError as e:
            return f"<h1>Error loading help content!</h1><p>Could not read file: {path}. Error: {e}</p>"
    else:
        return f"<h1>Help File Not Found</h1><p>Please create a file named '<b>{file_name}</b>' in the current directory.</p>"


def write_to_csv(file_name: Path, data: list[list[str]], headers: list[str]) -> None:
    # def write_to_csv(file_name: str, data: list[list[str]], headers: list[str]) -> None:
    # out_file = Path(settings.files.full_output_dir) / Path(file_name)
    # with open(out_file, "w", newline="", encoding="utf-8") as f:
    logger.info(f"Exporting records as csv to {file_name}")
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(headers)
        csvwriter.writerows(data)