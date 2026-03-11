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
    # {data-name: [
    # [col_name,
    # (brick height, brick length),
    # start-row (0-indexed),
    # start-col, widget-type]
    # , [display_titles]
    # ]}
    "art_cats": [
        [
            ("sublib", (1, 2), 0, 0, "combo"),
            ("langs", (1, 2), 0, 2, "line"),
            ("isbn", (1, 2), 0, 4, "line"),
            ("title", (2, 3), 1, 0, "text"),
            ("tr_title", (2, 3), 1, 3, "text"),
            ("subtitle", (2, 3), 3, 0, "text"),
            ("tr_subtitle", (2, 3), 3, 3, "text"),
            ("parallel_title", (2, 3), 5, 0, "text"),
            ("tr_parallel_title", (2, 3), 5, 3, "text"),
            ("parallel_subtitle", (2, 3), 7, 0, "text"),
            ("tr_parallel_subtitle", (2, 3), 7, 3, "text"),
            ("country_name", (1, 2), 13, 0, "line"),
            ("place", (1, 4), 13, 2, "line"),
            ("publisher", (1, 4), 14, 0, "line"),
            ("pub_year", (1, 1), 14, 4, "line"),
            ("copyright", (1, 1), 14, 5, "line"),
            ("pagination", (1, 1), 15, 1, "line"),
            ("size", (1, 1), 15, 0, "line"),
            ("illustrations", (1, 1), 15, 3, "combo"),
            ("series_title", (1, 3), 12, 0, "line"),
            ("series_enum", (1, 2), 12, 3, "line"),
            ("volume", (1, 1), 12, 5, "line"),
            ("notes", (3, 3), 9, 0, "text"),
            ("sales_code", (1, 1), 15, 2, "line"),
            ("sale_dates", (1, 2), 15, 4, "line"),
            ("hol_notes", (3, 3), 9, 3, "text"),
            ("donation", (1, 4), 16, 0, "line"),
            ("barcode", (1, 2), 16, 4, "line"),
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
            ("COL.langs", (1, 2), 0, 0, "line"),
            ("COL.isbn", (1, 2), 0, 2, "line"),
            ("COL.title", (2, 3), 1, 0, "text"),
            ("COL.subtitle", (2, 3), 1, 3, "text"),
            ("COL.artist", (1, 2), 0, 4, "line"),
            ("COL.place", (1, 3), 3, 0, "line"),
            ("COL.country_name", (1, 3), 3, 3, "line"),
            ("COL.publisher", (1, 2), 4, 0, "line"),
            ("COL.pub_year", (1, 1), 4, 2, "line"),
            ("COL.copyright", (1, 1), 4, 3, "line"),
            ("COL.pagination", (1, 1), 4, 4, "line"),
            ("COL.size", (1, 1), 4, 5, "line"),
            ("COL.notes", (2, 2), 6, 0, "text"),
            ("COL.authors", (1, 4), 5, 0, "line"),
            ("COL.call_number", (1, 2), 5, 4, "line"),
            ("COL.hol_notes", (2, 2), 6, 2, "text"),
            ("COL.barcode", (1, 2), 7, 4, "line"),
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
            ("Subject_consultant", (1, 2), 0, 0, "combo"),
            ("Fund_code", (1, 2), 1, 0, "combo"),
            ("Order_type", (1, 2), 2, 0, "combo"),
            ("Bib_info", (2, 6), 3, 0, "text"),
            ("Creator", (1, 2), 7, 0, "line"),
            ("Date", (1, 2), 7, 2, "line"),
            ("Isbn", (1, 2), 7, 4, "line"),
            ("Library", (1, 2), 0, 2, "combo"),
            ("Location", (1, 2), 1, 2, "combo"),
            ("Item_policy", (1, 2), 2, 2, "combo"),
            ("Reporting_code_1", (1, 2), 0, 4, "combo"),
            ("Reporting_code_2", (1, 2), 1, 4, "combo"),
            ("Reporting_code_3", (1, 2), 2, 4, "combo"),
            ("Hold_for", (1, 2), 8, 0, "line"),
            ("Notify", (1, 2), 9, 0, "line"),
            ("Additional_info", (2, 4), 8, 2, "text"),
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
