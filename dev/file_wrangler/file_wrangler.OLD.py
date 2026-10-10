from pathlib import Path
import pandas as pd
from pydantic import BaseModel, model_validator
from dataclasses import dataclass, field
from typing import TypedDict
import unicodedata
import yaml


class PipelineSpec(BaseModel):
    file_path_str: str
    file_path: None | Path
    file_extension: None | str #Optional[str]
    ideal_order: list[str]
    split_cols: list[tuple[str, str]]
    drop_cols: list[str]
    new_cols: list[tuple[str, str]]

    @model_validator(mode="after")
    def compute_file_path(self) -> "PipelineSpec":
        # Automatically populates file_path using the string value
        if self.file_path_str and not self.file_path:
            self.file_path = Path(self.file_path_str)
        return self


spec = PipelineSpec(
    file_path_str="./input_files/multilingual.csv",
    file_path=None,
    file_extension="",
    ideal_order=[
        "ID",
        "Extracted_ID",
        "First",
        "Last",
        "Location",
        "Country",
    ],
    split_cols=[
        (
            "Full_Name",
            # r"(?P<First>\w+)_(?P<Last>\w+)\s+\(ID:\s+(?P<Extracted_ID>\d+)\)"
            # Updated pattern: allows spaces around the underscore and captures all Unicode letters
            r"(?P<First>[^\s_]+)\s*_\s*(?P<Last>[^\s_]+)\s*\(ID:\s*(?P<Extracted_ID>\d+)\)",
        ),
    ],
    drop_cols=["Full_Name", "Age"],
    new_cols=[("Country", "UK")],
)


def get_data_frame(spec: PipelineSpec) -> tuple[pd.DataFrame, PipelineSpec]:
    spec.file_path = Path(spec.file_path_str)
    # file_path = Path(spec.file_path_str)
    file_extension = spec.file_path.suffix.lower()

    # 1. Load data forcing ALL columns to be interpreted as strings by default
    # This completely protects ISBNs, zip codes, and IDs from dropping leading zeros
    if file_extension == ".csv":
        df = pd.read_csv(spec.file_path, encoding="utf-8-sig", dtype=str)
    elif file_extension in [".xlsx", ".xls"]:
        df = pd.read_excel(spec.file_path, dtype=str)
    else:
        raise ValueError(
      f"Unsupported file format: {file_extension}. Please use CSV or Excel."
    )

    # 2. Standardize and normalize all string columns (Handles French, German, Chinese)
    for col in df.select_dtypes(include=["object", "string"]).columns:
        # df[col] = df[col].fillna("").astype(str).str.normalize("NFC").str.strip()
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
  output_path = spec.file_path.with_suffix(f".new{spec.file_extension}")

  # 8. Save the file back into its original format
  if spec.file_extension == ".csv":
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
  elif spec.file_extension in [".xlsx", ".xls"]:
    df.to_excel(output_path, index=False)

  print(f"Success! Saved multi-language processed data to: {output_path}")


def split_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
  # 4. Split a column according to a regex pattern
  # regex_pattern = r"(?P<First>\w+)_(?P<Last>\w+)\s+\(ID:\s+(?P<Extracted_ID>\d+)\)"
  for name, pattern in spec.split_cols:
    if  name in df.columns:
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


def rearrange_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
  existing_order = [col for col in spec.ideal_order if col in df.columns]
  return df[existing_order]


# def wrangle_data(file_path_str):
def wrangle_data(spec: PipelineSpec):
  df, spec = get_data_frame(spec)

  # --- [Your Data Wrangling Logic Starts Here] ---

  df = add_columns(df, spec)
  df = split_columns(df, spec)
  df = drop_columns(df, spec)
  df = rearrange_columns(df, spec)

  # --- [Your Data Wrangling Logic Ends Here] ---

  save_data_frame(df, spec)


# wrangle_data("./input_files/multilingual.csv")
wrangle_data(spec)
