"""Data Wrangling Pipeline Script.

This script reads a multilingual CSV or Excel file, normalizes
all Unicode character sets (supporting CJK, Cyrillic, Hindi, and Arabic),
applies dynamic column modifications and regex extractions based on
an external YAML configuration file, and exports the clean data either in the
original format or as specified in the external yaml file.
"""

from pathlib import Path
from typing import Optional
import unicodedata
import yaml
import pandas as pd
from pydantic import BaseModel, model_validator


class PipelineSpec(BaseModel):
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
    # to perfectly align with the data model's structural type hints.
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
        df = pd.read_excel(spec.file_path, dtype=str)
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


def rearrange_columns(df: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    existing_order = [col for col in spec.ideal_order if col in df.columns]
    return df[existing_order]


def wrangle_data(spec: PipelineSpec):
    df, spec = get_data_frame(spec)
    df = add_columns(df, spec)
    df = split_columns(df, spec)
    df = drop_columns(df, spec)
    df = rearrange_columns(df, spec)
    save_data_frame(df, spec)


# --- Application Entry Point ---
if __name__ == "__main__":
    try:
        # Load the configuration dynamically
        config_spec = load_spec_from_yaml("./dev/file_wrangler/multilingual.yaml")

        # Execute processing loop
        wrangle_data(config_spec)
    except Exception as e:
        print(f"Pipeline Execution Failed: {e}")
