"""Data Wrangling Pipeline Script.

This script reads a multilingual CSV or Excel file, normalizes
all Unicode character sets (supporting CJK, Cyrillic, Hindi, and Arabic),
applies dynamic column modifications and regex extractions based on
an external YAML configuration file, and exports the clean data either in the
original format or as specified in the external yaml file.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import unicodedata
import yaml
import pandas as pd
from pydantic import BaseModel, model_validator


class PipelineSpec(BaseModel):
  spec_name: str
  file_path_str: str
  file_path: Optional[Path] = None
  file_extension: Optional[str] = None
  ideal_order: list[str]
  split_cols: list[tuple[str, str]]
  drop_cols: list[str]
  new_cols: list[tuple[str, str]]

  @model_validator(mode="after")
  def compute_file_path(self) -> "PipelineSpec":
      if self.file_path_str and not self.file_path:
          self.file_path = Path(self.file_path_str)
      return self


def load_spec_from_yaml(yaml_path_str: str) -> PipelineSpec:
    """Loads and formats a YAML file into a validated PipelineSpec model."""
    yaml_path = Path(yaml_path_str)
    if not yaml_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {yaml_path}")

    # 1. Parse raw YAML
    raw_data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    # 2. YAML parses nested sequences as lists. We cast them to tuples
    # to align with the data model's structural type hints.
    if "split_cols" in raw_data:
        raw_data["split_cols"] = [tuple(item) for item in raw_data["split_cols"]]
    if "new_cols" in raw_data:
        raw_data["new_cols"] = [tuple(item) for item in raw_data["new_cols"]]

    # 3. Hydrate and validate the model
    return PipelineSpec.model_validate(raw_data)


def get_data_frame(spec: PipelineSpec) -> tuple[pd.DataFrame, PipelineSpec]:
    spec.file_path = Path(spec.file_path_str)
    file_extension = spec.file_path.suffix.lower()

    if file_extension == ".csv":
        df = pd.read_csv(spec.file_path, encoding="utf-8-sig", dtype=str)
    elif file_extension in [".xlsx", ".xls"]:
        df = pd.read_excel(spec.file_path, header=0, dtype=str)
        # df = pd.read_excel(spec.file_path, header=1, dtype=str)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}.")

    # Multi-language string validation loop
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .apply(lambda x: unicodedata.normalize("NFC", x).strip())
        )

    if not spec.file_extension:
        spec.file_extension = file_extension
    return df, spec


def save_data_frame(df: pd.DataFrame, spec: PipelineSpec) -> None:
    if spec.file_path is None:
        raise ValueError("File path was never resolved or initialized.")

    output_path = spec.file_path.with_suffix(f".new{spec.file_extension}")

    if spec.file_extension == ".csv":
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
    elif spec.file_extension in [".xlsx", ".xls"]:
        df.to_excel(output_path, index=False)

    print(f"Success! Saved multi-language processed data to: {output_path}")


def split_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    for name, pattern in spec.split_cols:
        if name in df.columns:
            extracted_data = df[name].str.extract(pattern)
            df = pd.concat([df, extracted_data], axis=1)
    return df


def add_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    for col_name, default_value in spec.new_cols:
        df[col_name] = default_value
    return df


def drop_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    df = df.drop(columns=spec.drop_cols, errors="ignore")
    return df


# def rearrange_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
#     existing_order = [col for col in spec.ideal_order if col in df.columns]
#     return df[existing_order]


def rearrange_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    existing_order = []
    rename_mapping = {}
    separator = "===>"

    for item in spec.ideal_order:
        # Check if the configuration item specifies a rename rule
        if separator in item:
            original_name, new_name = item.split(separator , 1)
            original_name = original_name.strip()
            new_name = new_name.strip()
        else:
            original_name = item
            new_name = None

        # If the column exists in the DataFrame, queue it for rearrangement
        if original_name in df.columns:
            existing_order.append(original_name)
            if new_name:
                rename_mapping[original_name] = new_name

    # 1. Rearrange the columns to the specified order
    df = df[existing_order]

    # 2. Rename the specified columns in-place
    if rename_mapping:
        df = df.rename(columns=rename_mapping)

    return df


def wrangle_data(spec: PipelineSpec):
    df, spec = get_data_frame(spec)
    df = add_columns(df, spec)
    df = split_columns(df, spec)
    df = drop_columns(df, spec)
    df = rearrange_columns(df, spec)
    save_data_frame(df, spec)


import argparse
import sys

if __name__ == "__main__":
    # 1. Create a terminal argument parser
    parser = argparse.ArgumentParser(
        description="Data Wrangler Pipeline: Processes multi-language CSV/Excel data."
    )

    # 2. Positional argument for the target data file path
    parser.add_argument(
        "file_path",
        help="Path to the input CSV or Excel file to process.",
    )

    # 3. Add the --new / -n boolean flag switch
    parser.add_argument(
        "--new",
        "-n",
        action="store_true",  # Makes the argument act as a true/false toggle flag
        help="Inspect a new file: print out headers and the first 5 rows, then exit without processing.",
    )

    args = parser.parse_args()

    try:
        # --- PATH PRE-RESOLUTION ---
        # Construct a temporary PipelineSpec mock shell to leverage your get_data_frame function
        # This guarantees your multi-language string normalizations run before previewing!
        preview_spec = PipelineSpec(
            spec_name="Preview Shell",
            file_path_str=args.file_path,
            ideal_order=[],
            split_cols=[],
            drop_cols=[],
            new_cols=[],
        )

        # 4. CONDITIONAL FLAG CHECK: If --new or -n is typed in the command line
        if args.new:
            print(f"\n=================== INSPECTING NEW FILE ===================")
            print(f"Target File: {args.file_path}")

            # Load and normalize the data array structure
            df, _ = get_data_frame(preview_spec)

            print(f"\n--- DETECTED HEADERS ({len(df.columns)} total) ---")
            print(list(df.columns))

            print(f"\n--- FIRST 5 ROWS PREVIEW ---")
            print(df.head(5).to_string())
            print(f"===========================================================\n")

            # Terminate execution gracefully
            sys.exit(0)

        # --- STANDARD WORKFLOW ---
        # 5. Load your global settings schema from the static YAML location
        config_spec = load_spec_from_yaml("./dev/file_wrangler/specifications.yaml")

        # 6. Override the default YAML path string with your command-line parameter path
        config_spec.file_path_str = args.file_path

        # Re-trigger Pydantic validation hook to refresh the path parameters cleanly
        config_spec = PipelineSpec.model_validate(config_spec.model_dump())

        # 7. Run the full analytical pipeline loops
        wrangle_data(config_spec)

    except SystemExit:
        # Catch standard sys.exit(0) steps so they don't print as pipeline execution failures
        pass
    except Exception as e:
        print(f"Pipeline Execution Failed: {e}")
        sys.exit(1)


# if __name__ == "__main__":
#     # 1. Create a terminal argument parser
#     parser = argparse.ArgumentParser(
#         description="Data Wrangler Pipeline: Processes multi-language CSV/Excel data."
#     )

#     # 2. Add an optional/required file path argument flag
#     parser.add_argument(
#         "file_path",
#         nargs="?",  # Makes it optional so it falls back gracefully if omitted
#         help="Path to the input CSV or Excel file to process.",
#     )

#     args = parser.parse_args()
#     try:
#         # Load the configuration dynamically
#         config_spec = load_spec_from_yaml("./dev/file_wrangler/specifications.yaml")
#         if args.file_path:
#             config_spec.file_path_str = args.file_path
#             # Re-trigger Pydantic validation hook to build the fresh Path object
#             config_spec = PipelineSpec.model_validate(config_spec.model_dump())

#         # Execute processing loop
#         wrangle_data(config_spec)
#     except Exception as e:
#         print(f"Pipeline Execution Failed: {e}")
