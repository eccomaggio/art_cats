"""
Order form for TAY / ART libraries to replace excel-based form.
Contact: Ross Jones, Osney One
"""

import logging
from . import utils

from enum import Enum
from pathlib import Path
from .settings import Settings
from . import common

# logger = logging.getLogger(__name__)


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

    Subject_consultant = "Subject consultant"
    Fund_code = "Fund code"
    Order_type = "Order type"
    Bib_info = "Bibliographic information"
    Creator = "Creator"
    Date = "Publishing date"
    Isbn = "ISBN"
    Library = "Library"
    Location = "Location"
    Item_policy = "Item policy"
    Reporting_code_1 = "Reporting code 1"
    Reporting_code_2 = "Reporting code 2"
    Reporting_code_3 = "Reporting code 3"
    Hold_for = "Hold for"
    Notify = "Notify"
    Additional_info = "Additional order instructions"


##### Tailor settings

settings = Settings()
settings.title = "order_form"
settings.headers = [member.display_title for member in COL]
settings.show_table_view = True
settings.locking_is_enabled = False
settings.combos.data_file = "combo_data.yaml"

settings.validation.fields_to_clear = [
    COL.Isbn,
    COL.Reporting_code_1,
    COL.Reporting_code_2,
    COL.Reporting_code_3,
    COL.Notify,
    COL.Hold_for,
    COL.Bib_info,
    COL.Additional_info,
]
settings.validation.fields_to_fill = [
    [],
]
settings.validation.required_fields = [
    COL.Subject_consultant.name,
    COL.Fund_code.name,
    COL.Order_type.name,
    COL.Bib_info.name,
    COL.Library.name,
    COL.Location.name,
    COL.Item_policy.name,
    COL.Bib_info.name,
]
settings.validation.validate_always = []
settings.validation.validate_if_present = [
    COL.Isbn.name,
    COL.Hold_for.name,
    COL.Notify.name,
]
settings.validation.validation_skip_fieldname = COL.Additional_info.name


settings.combos.independents = [
    COL.Subject_consultant.name,
    COL.Order_type.name,
    COL.Library.name,
    COL.Item_policy.name,
    COL.Reporting_code_1.name,
    COL.Reporting_code_2.name,
    COL.Reporting_code_3.name,
]
settings.combos.leaders = [COL.Subject_consultant.name, COL.Library.name]
settings.combos.followers = [COL.Fund_code.name, COL.Location.name]
settings.combos.dict_by_follower = {
    key: value
    for key, value in list(zip(settings.combos.followers, settings.combos.leaders))
}
settings.combos.dict_by_leader = {
    key: value
    for key, value in list(zip(settings.combos.leaders, settings.combos.followers))
}
settings.default_template = [
    ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col, widget-type=line/area/drop]
    (COL.Subject_consultant, "1:2", 0, 0, "combo"),
    (COL.Fund_code, "1:2", 1, 0, "combo"),
    (COL.Order_type, "1:2", 2, 0, "combo"),
    (COL.Bib_info, "2:6", 3, 0, "text"),
    (COL.Creator, "1:2", 7, 0, "line"),
    (COL.Date, "1:2", 7, 2, "line"),
    (COL.Isbn, "1:2", 7, 4, "line"),
    (COL.Library, "1:2", 0, 2, "combo"),
    (COL.Location, "1:2", 1, 2, "combo"),
    (COL.Item_policy, "1:2", 2, 2, "combo"),
    (COL.Reporting_code_1, "1:2", 0, 4, "combo"),
    (COL.Reporting_code_2, "1:2", 1, 4, "combo"),
    (COL.Reporting_code_3, "1:2", 2, 4, "combo"),
    (COL.Hold_for, "1:2", 8, 0, "line"),
    (COL.Notify, "1:2", 9, 0, "line"),
    (COL.Additional_info, "2:4", 8, 2, "text"),
]
# print(f"++++ ++++ ++++ {settings.combos.dict_by_follower=}")

settings.files.help_file = "help_order_form.html"
settings.files.output_dir = Path("your_order")
settings.files.full_output_dir = settings.files.module_dir / settings.files.output_dir
if settings.create_output_dir:
    settings.files.full_output_dir.mkdir(exist_ok=True)


CUSTOM_LOG_FILE = settings.files.full_output_dir / "logger.log"
utils.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
logger = logging.getLogger(__name__)

def main():
    common.run(settings, COL)

if __name__ == "__main__":
    # common.run(settings, COL)
    main()