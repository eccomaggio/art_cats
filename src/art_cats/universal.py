"""
Order form for TAY / ART libraries to replace excel-based form.
Contact: Ross Jones, Osney One
"""

# import logging
from . import log_setup

from enum import Enum
from pathlib import Path
from .settings import Default_settings
from . import form_gui

# logger = logging.getLogger(__name__)


def main():
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

        # Subject_consultant = "Subject consultant"
        # Fund_code = "Fund code"
        # Order_type = "Order type"
        # Bib_info = "Bibliographic information"
        # Creator = "Creator"
        # Date = "Publishing date"
        # Isbn = "ISBN"
        # Library = "Library"
        # Location = "Location"
        # Item_policy = "Item policy"
        # Reporting_code_1 = "Reporting code 1"
        # Reporting_code_2 = "Reporting code 2"
        # Reporting_code_3 = "Reporting code 3"
        # Hold_for = "Hold for"
        # Notify = "Notify"
        # Additional_info = "Additional order instructions"

    ##### Tailor settings

    settings = Default_settings()
    settings.title = "universal"
    # settings.headers = [member.display_title for member in COL]
    settings.show_table_view = True
    settings.locking_is_enabled = False
    settings.use_default_layout = False

    settings.validation.fields_to_clear = [
        # COL.Isbn,
    ]

    settings.validation.required_fields = [
        # COL.Subject_consultant.name,
    ]

    settings.validation.must_validate = [
        # COL.Isbn.name,
    ]

    settings.combos.independents = [
        # COL.Subject_consultant.name,
    ]

    # settings.default_template = [
    #     ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col, widget-type=line/area/drop]
    #     (COL.Subject_consultant, (1, 2), 0, 0, "combo"),
    #     (COL.Fund_code, (1, 2), 1, 0, "combo"),
    #     (COL.Order_type, (1, 2), 2, 0, "combo"),
    #     (COL.Bib_info, (2, 6), 3, 0, "text"),
    #     (COL.Creator, (1, 2), 7, 0, "line"),
    #     (COL.Date, (1, 2), 7, 2, "line"),
    #     (COL.Isbn, (1, 2), 7, 4, "line"),
    #     (COL.Library, (1, 2), 0, 2, "combo"),
    #     (COL.Location, (1, 2), 1, 2, "combo"),
    #     (COL.Item_policy, (1, 2), 2, 2, "combo"),
    #     (COL.Reporting_code_1, (1, 2), 0, 4, "combo"),
    #     (COL.Reporting_code_2, (1, 2), 1, 4, "combo"),
    #     (COL.Reporting_code_3, (1, 2), 2, 4, "combo"),
    #     (COL.Hold_for, (1, 2), 8, 0, "line"),
    #     (COL.Notify, (1, 2), 9, 0, "line"),
    #     (COL.Additional_info, (2, 4), 8, 2, "text"),
    # ]

    # settings.files.help_file = "html/help_order_form.html"
    settings.files.full_output_dir = (
        settings.files.module_dir / settings.files.output_dir
    )

    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    CUSTOM_LOG_FILE = (
        settings.files.full_output_dir / "logger.log"
    )

    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
    form_gui.run(settings, COL)


if __name__ == "__main__":
    main()
