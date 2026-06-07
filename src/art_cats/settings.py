"""
Load default settings: many will be overwritten by entry-point scripts
(in this case: art.py & order.py)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Files:
    app_dir: Path = Path("src/art_cats")
    data_dir: Path = Path("input_files")  # where the file dialog opens to
    module_dir: Path = Path(__file__).parent.parent.parent.parent
    output_dir: Path = Path("output_files")
    # full_output_dir: Path = Path(__file__).parent  # module_dir / output_dir
    help_file: str = "html/help_default.html"
    backup_file: str = "backup.bak"
    in_file: str = ""
    out_file: str = "new_file"
    default_output_filename: str = "output"

    @property
    def full_output_dir(self) -> Path:
        return self.module_dir / self.output_dir


@dataclass
class Validation:
    fields_to_autofill_info: dict = field(default_factory=dict)
    fields_to_autofill: list = field(default_factory=list)
    required_fields: list = field(default_factory=list)
    must_validate: list = field(default_factory=list)
    fields_to_clear: list = field(default_factory=list)
    mandatory_marc_fields: dict = field(default_factory=dict)
    clear_all_fields: bool = True
    validation_skip_fieldname: str = ""
    validation_skip_text: str = "*dummy*"
    # check_for_duplicates: bool = False
    ensure_these_cols_have_unique_values: list = field(default_factory=list)


@dataclass
class Styles:
    text_changed: str = "background-color: mistyrose; border: 1px solid silver;"
    text_changed_border_only: str = "border: 1px solid red;"
    validation_error: str = "border: 2px solid red;"
    border_only_active: str = "border: 1px solid whitesmoke;"
    labels: str = "font-weight: bold;"
    label_active: str = "color: #7c6241;"
    label_locked: str = "color: darkgrey;"
    input_active: str = "border: 1px solid lightgrey; background-color: white;"
    input_locked: str = "border: 1px solid whitesmoke; background-color: whitesmoke;"
    combo_dropdown: str = (
        "QComboBox QAbstractItemView {selection-background-color: #3B82F6; selection-color: white;}"
    )


@dataclass
class Labels:
    show_help: str = "show help"
    hide_help: str = "hide help"


@dataclass
class Combos:
    independents: list = field(default_factory=list)
    leaders: list = field(default_factory=list)
    followers: list = field(default_factory=list)
    dict_by_follower: dict = field(default_factory=dict)
    dict_by_leader: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    default_text: str = "[Choose]"
    following_default_text: str = " (first select "
    data_file: str = ""


@dataclass
class Default_settings:
    files: Files = field(default_factory=Files)
    validation: Validation = field(default_factory=Validation)
    combos: Combos = field(default_factory=Combos)
    template: list = field(default_factory=list)
    title: str = "default"

    is_existing_file: bool = False
    file_newly_created: bool = False
    use_default_layout: bool = True
    show_marc_button: bool = False
    column_names: list = field(default_factory=list)
    csv_to_marc_mappings: list = field(default_factory=list)
    layout_template: list = field(default_factory=list)
    first_row_is_header: bool = True

    field_split_marker: str = "*//*"
    blank: str = " "
    styles: Styles = field(default_factory=Styles)
    labels: Labels = field(default_factory=Labels)
    locking_is_enabled: bool = True
    show_table_view: bool = True
    auto_submit_form_on_x_field: bool = False
    auto_submit_form_field_name: str = ""
    auto_submit_form_field: Any = None
    create_output_dir: bool = True
    create_chu_file: bool = True
    create_excel_file: bool = True

    timestamp: str = (
        str(datetime.now(timezone.utc))
        .split(".")[0]
        .replace(" ", "_")
        .replace(":", "-")
    )

    known_patterns: dict = field(default_factory=dict)
