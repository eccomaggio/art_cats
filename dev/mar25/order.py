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

        subject_consultant = "Subject consultant"
        fund_code = "Fund code"
        order_type = "Order type"
        bib_info = "Bibliographic information"
        creator = "Creator"
        date = "Publishing date"
        isbn = "ISBN"
        library = "Library"
        location = "Location"
        item_policy = "Item policy"
        reporting_code_1 = "Reporting code 1"
        reporting_code_2 = "Reporting code 2"
        reporting_code_3 = "Reporting code 3"
        hold_for = "Hold for"
        notify = "Notify"
        additional_info = "Additional order instructions"

    ##### Tailor settings

    settings = Default_settings()
    settings.title = "order_form"
    # settings.column_names = [column.name for column in COL]
    # settings.headers = [member.display_title for member in COL]
    settings.show_table_view = True
    settings.locking_is_enabled = False
    settings.combos.data_file = "data/combo_data.yaml"

    settings.validation.fields_to_clear = [
        COL.isbn,
        COL.reporting_code_1,
        COL.reporting_code_2,
        COL.reporting_code_3,
        COL.notify,
        COL.hold_for,
        COL.bib_info,
        COL.additional_info,
    ]

    # settings.validation.fields_to_fill = {}
    settings.validation.required_fields = [
        COL.subject_consultant.name,
        COL.fund_code.name,
        COL.order_type.name,
        COL.bib_info.name,
        COL.library.name,
        COL.location.name,
        COL.item_policy.name,
        COL.bib_info.name,
    ]

    # settings.validation.validate_always = []
    # settings.validation.validate_if_present = [
    settings.validation.must_validate = [
        COL.isbn.name,
        COL.hold_for.name,
        COL.notify.name,
    ]

    settings.validation.validation_skip_fieldname = COL.additional_info.name

    settings.combos.independents = [
        COL.subject_consultant.name,
        COL.order_type.name,
        COL.library.name,
        COL.item_policy.name,
        COL.reporting_code_1.name,
        COL.reporting_code_2.name,
        COL.reporting_code_3.name,
    ]

    settings.combos.leaders = [COL.subject_consultant.name, COL.library.name]

    settings.combos.followers = [COL.fund_code.name, COL.location.name]

    settings.combos.dict_by_follower = dict(
        list(zip(settings.combos.followers, settings.combos.leaders))
    )

    settings.combos.dict_by_leader = dict(
        list(zip(settings.combos.leaders, settings.combos.followers))
    )

    settings.template = [
        ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col, widget-type=line/area/drop]
        (COL.subject_consultant, (1, 2), 0, 0, "combo"),
        (COL.fund_code, (1, 2), 1, 0, "combo"),
        (COL.order_type, (1, 2), 2, 0, "combo"),
        (COL.bib_info, (2, 6), 3, 0, "text"),
        (COL.creator, (1, 2), 7, 0, "line"),
        (COL.date, (1, 2), 7, 2, "line"),
        (COL.isbn, (1, 2), 7, 4, "line"),
        (COL.library, (1, 2), 0, 2, "combo"),
        (COL.location, (1, 2), 1, 2, "combo"),
        (COL.item_policy, (1, 2), 2, 2, "combo"),
        (COL.reporting_code_1, (1, 2), 0, 4, "combo"),
        (COL.reporting_code_2, (1, 2), 1, 4, "combo"),
        (COL.reporting_code_3, (1, 2), 2, 4, "combo"),
        (COL.hold_for, (1, 2), 8, 0, "line"),
        (COL.notify, (1, 2), 9, 0, "line"),
        (COL.additional_info, (2, 4), 8, 2, "text"),
    ]

    settings.files.help_file = "html/help_order_form.html"
    settings.files.output_dir = Path("your_order")
    settings.files.full_output_dir = (
        settings.files.module_dir / settings.files.output_dir
    )

    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    headers = [member.display_title for member in COL]
    CUSTOM_LOG_FILE = (
        # settings.files.full_output_dir / f"logger.{settings.timestamp}.log"
        settings.files.full_output_dir
        / "logger.log"
    )

    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
    form_gui.run(settings, headers, COL)


if __name__ == "__main__":
    main()
