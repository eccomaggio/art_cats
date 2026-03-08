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


known_types = {
    # {title: [ [col_names], [display_titles] ]}
    "art_cats": [
        [
            "sublib",
            "langs",
            "isbn",
            "title",
            "tr_title",
            "subtitle",
            "tr_subtitle",
            "parallel_title",
            "tr_parallel_title",
            "parallel_subtitle",
            "tr_parallel_subtitle",
            "country_name",
            "place",
            "publisher",
            "pub_year",
            "copyright",
            "pagination",
            "size",
            "illustrations",
            "series_title",
            "series_enum",
            "volume",
            "notes",
            "sales_code",
            "sale_dates",
            "hol_notes",
            "donation",
            "barcode",
            ],

        [
            "Library",
            "language of resource",
            "ISBN",
            "Title",
            "Title transliteration",
            "Subtitle",
            "Subtitle transliteration",
            "Parallel title (dual language only)",
            "Parallel title transliteration",
            "Parallel subtitle (dual language only)",
            "Parallel subtitle transliteration",
            "Country of publication",
            "(State,) City of publication",
            "Publisher's name",
            "Year of publication",
            "Year of copyright",
            "Number of pages",
            "Size (height)",
            "Illustrations",
            "Series title",
            "Series enumeration",
            "Volume",
            "Note",
            "Sale code",
            "Date of auction",
            "HOL notes",
            "Donor note",
            "Barcode",
            ]
        ],

    "strachan": [
        [
            "langs",
            "isbn",
            "title",
            "subtitle",
            "artist",
            "place",
            "country_name",
            "publisher",
            "pub_year",
            "copyright",
            "pagination",
            "size",
            "notes",
            "authors",
            "call_number",
            "hol_notes",
            "barcode",
        ],

        [
            "Language of resource",
            "ISBN",
            "Title",
            "Subtitle",
            "Artist",
            "(State,) City of publication",
            "Country of publication",
            "Publisher's name",
            "Year of publication",
            "Year of copyright",
            "Pagination",
            "Size",
            "Note",
            "Author(s)",
            "Call number",
            "Holding note",
            "Barcode",],
        ],

    "orders": [
        [
            "Subject_consultant",
            "Fund_code",
            "Order_type",
            "Bib_info",
            "Creator",
            "Date",
            "Isbn",
            "Library",
            "Location",
            "Item_policy",
            "Reporting_code_1",
            "Reporting_code_2",
            "Reporting_code_3",
            "Hold_for",
            "Notify",
            "Additional_info",
        ],

        [
            "Subject consultant",
            "Fund code",
            "Order type",
            "Bibliographic information",
            "Creator",
            "Publishing date",
            "ISBN",
            "Library",
            "Location",
            "Item policy",
            "Reporting code 1",
            "Reporting code 2",
            "Reporting code 3",
            "Hold for",
            "Notify",
            "Additional order instructions",
        ],
    ],
}


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

    ##### Tailor settings

    settings = Default_settings()
    settings.title = "universal"
    settings.known_types = known_types
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
