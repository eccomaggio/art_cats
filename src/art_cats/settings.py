from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Files:
    in_file_full = ""
    in_file = ""
    out_file = "new_file"
    default_output_filename = "output"
    # app_dir = "app"
    app_dir = Path("src/art_cats")
    data_dir = Path("input_files")
    output_dir = Path("output_files")
    help_file = "help.html"
    backup_file = "backup.bak"


@dataclass
class Validation:
    fields_to_clear = []
    fields_to_fill = [
        # E.G. [COL.sublib, "ARTBL"],
        [],
    ]
    required_fields = []
    validate_always = []
    validate_if_present = []
    validation_skip_field = None
    validation_skip_text = "*dummy*"


@dataclass
class Styles:
    text_changed = "border: 1px solid red; background-color: white;"
    text_changed_border_only = "border: 1px solid red;"
    border_only_active = "border: 1px solid whitesmoke;"
    labels = "font-weight: bold;"
    label_active = "color: #7c6241;"
    label_locked = "color: darkgrey;"
    input_active = "border: 1px solid lightgrey; background-color: white;"
    input_locked = "border: 1px solid whitesmoke; background-color: whitesmoke;"
    combo_dropdown = "QComboBox QAbstractItemView {selection-background-color: #3B82F6; selection-color: white;}"


@dataclass
class Labels:
    show_help = "show help"
    hide_help = "hide help"


@dataclass
class Combos:
    default_text = " >> Choose <<"
    following_default_text = " (first select "
    independents = []
    leaders = []
    followers = []
    dict_by_follower = {}
    dict_by_leader = {}
    data = []
    data_file = ""

@dataclass
class Settings:
    title= "art_catalogue"
    is_existing_file = True
    use_default_layout = True
    # layout_template: tuple = ()
    layout_template = []
    first_row_is_header = True

    alt_title_signifier = "*//*"
    # headers = [member.display_title for member in COL]
    headers = []
    files = Files()
    validation = Validation()
    combos = Combos()
    styles = Styles()
    labels = Labels()
    locking_is_enabled = True
    show_table_view = True
    default_template = ()
