"""
Load default settings: many will be overwritten by entry-point scripts
(in this case: art.py & order.py)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from datetime import datetime, timezone


# class COL(Enum):
#     pass


# NB. these are simply defaults; most are overwritten by the entry files.
@dataclass
class Files:
    app_dir = Path("src/art_cats")
    data_dir = Path("input_files")  # where the file dialog opens to
    module_dir = Path(__file__).parent.parent.parent.parent
    output_dir = Path("output_files")
    full_output_dir = Path(__file__).parent  # module_dir / output_dir
    help_file = "help.html"
    backup_file = "backup.bak"
    # in_file_full = ""
    in_file = ""
    out_file = "new_file"
    default_output_filename = "output"


@dataclass
class Validation:
    fields_to_clear = []
    fields_to_fill_info = {
        # [COL.sublib.name : "ARTBL",
    }
    fields_to_fill = []
    required_fields = []
    must_validate = []
    # validate_always = []
    # validate_if_present = []
    # validation_skip_field: 'COL' = field(default=None)
    validation_skip_fieldname = ""
    validation_skip_text = "*dummy*"


@dataclass
class Styles:
    text_changed = "background-color: mistyrose; border: 1px solid silver;"
    text_changed_OLD = "border: 1px solid red; background-color: white;"
    # text_changed_checkbox = "QCheckBox::indicator {background-color: mistyrose; border: 1px solid silver;}"
    text_changed_border_only = "border: 1px solid red;"
    validation_error = "border: 2px solid red;"
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
    # data = []
    data = {}
    data_file = ""


@dataclass
class Default_settings:
    title = "art_catalogue"
    # is_existing_file = True
    is_existing_file = False
    use_default_layout = True
    show_marc_button = False
    # layout_template: tuple = ()
    layout_template = []
    first_row_is_header = True

    alt_title_signifier = "*//*"
    blank = " "
    # headers = [member.display_title for member in COL]
    headers = []
    files = Files()
    validation = Validation()
    combos = Combos()
    styles = Styles()
    labels = Labels()
    locking_is_enabled = True
    show_table_view = True
    #* These three allow the form to auto-submit when a specific field is completed
    auto_submit_form_on_x_field = False
    auto_submit_form_field_name = ""
    auto_submit_form_field: Any = None
    # submit_when_barcode_entered = False
    default_template = []
    create_output_dir = True
    create_chu_file = True
    create_excel_file = True
    timestamp = (
        str(datetime.now(timezone.utc))
        .split(".")[0]
        .replace(" ", "_")
        .replace(":", "-")
    )
