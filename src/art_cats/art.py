"""
GUI to replace excel files in the excel file cataloguing workflow. I wanted to avoid excel files as the automatic user input form is inadequate and coding a custom one is painful.
This can create a file from scratch or load a suitable (i.e. contains the correct number of fields in the correct order) csv or excel file. After adding and amending records, the result can be saved as a .csv file and / or marc 21 files (.mrk & .mrc files)
It builds on a script that converts excel files into markdown; in fact, the current script imports this script and utilises it to open files and create internal representations ("Records").
"""

# import logging
from . import log_setup

from enum import Enum
from pathlib import Path
from .settings import Default_settings
from . import form_gui
from . import marc_21

# logger = logging.getLogger(__name__)


def main():
    # marc_21.test_country_code()
    # quit()
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

        sublib = "Library"
        langs = "language of resource"
        isbn = "ISBN"
        title = "Title"
        tr_title = "Title transliteration"
        subtitle = "Subtitle"
        tr_subtitle = "Subtitle transliteration"
        parallel_title = "Parallel title (dual language only)"
        tr_parallel_title = "Parallel title transliteration"
        parallel_subtitle = "Parallel subtitle (dual language only)"
        tr_parallel_subtitle = "Parallel subtitle transliteration"
        country_name = "Country of publication"
        state = "State (US/UK/Canada & Australia only)"
        place = "Place of publication"
        publisher = "Publisher's name"
        pub_year = "Year of publication"
        copyright = "Year of copyright"
        extent = "Number of pages"
        size = "Size (height)"
        is_illustrated = "Illustrated"
        series_title = "Series title"
        series_enum = "Series enumeration"
        volume = "Volume"
        notes = "Note"
        sales_code = "Sale code"
        sale_dates = "Date of auction"
        hol_notes = "HOL notes"
        donation = "Donor note"
        barcode = "Barcode"

    ##### Tailor settings

    settings = Default_settings()
    settings.title = "art_catalogue"
    settings.headers = [member.display_title for member in COL]
    settings.show_table_view = False
    settings.locking_is_enabled = True
    settings.submit_when_barcode_entered = True

    settings.validation.fields_to_clear = [
        COL.barcode,
        COL.hol_notes,
        COL.extent,
        COL.pub_year,
        COL.sale_dates,
        COL.copyright,
        COL.sale_dates,
        COL.sales_code,
    ]
    settings.validation.fields_to_fill_info = {
        COL.sublib.name : "ARTBL",
    }
    settings.validation.fields_to_fill = list(settings.validation.fields_to_fill_info.keys())
    settings.validation.required_fields = [
        COL.langs.name,
        COL.title.name,
        COL.extent.name,
        COL.pub_year.name,
        COL.publisher.name,
        COL.country_name.name,
        COL.place.name,
        COL.extent.name,
        COL.size.name,
        COL.barcode.name,
    ]
    # settings.validation.validate_always = [COL.barcode.name]
    # settings.validation.validate_if_present = [COL.isbn.name]
    settings.validation.must_validate = [COL.barcode.name, COL.isbn.name]
    settings.validation.validation_skip_fieldname = COL.barcode.name

    # settings.default_template = [
    #     ## non-algorithmic version needs to be: [title, brick-type, start-row, start-col]
    #     ## needs to be in same order as COL specification
    #     (COL.sublib, "1:2", 0, 0, "line"),
    #     (COL.langs, "1:2", 0, 2, "line"),
    #     (COL.isbn, "1:2", 0, 4, "line"),
    #     (COL.title, "2:3", 1, 0, "text"),
    #     (COL.tr_title, "2:3", 1, 3, "text"),
    #     (COL.subtitle, "2:3", 3, 0, "text"),
    #     (COL.tr_subtitle, "2:3", 3, 3, "text"),
    #     (COL.parallel_title, "2:3", 5, 0, "text"),
    #     (COL.tr_parallel_title, "2:3", 5, 3, "text"),
    #     (COL.parallel_subtitle, "2:3", 7, 0, "text"),
    #     (COL.tr_parallel_subtitle, "2:3", 7, 3, "text"),
    #     (COL.country_name, "1:2", 13, 0, "line"),
    #     (COL.state, "1:2", 13, 2, "line"),
    #     (COL.place, "1:2", 13, 4, "line"),
    #     (COL.publisher, "1:4", 14, 0, "line"),
    #     (COL.pub_year, "1:1", 14, 4, "line"),
    #     (COL.copyright, "1:1", 14, 5, "line"),
    #     (COL.extent, "1:1", 15, 1, "line"),
    #     (COL.size, "1:1", 15, 0, "line"),
    #     (COL.is_illustrated, "1:1", 15, 3, "checkbox"),
    #     (COL.series_title, "1:3", 12, 0, "line"),
    #     (COL.series_enum, "1:2", 12, 3, "line"),
    #     (COL.volume, "1:1", 12, 5, "line"),
    #     (COL.notes, "3:3", 9, 0, "text"),
    #     (COL.sales_code, "1:1", 15, 2, "line"),
    #     (COL.sale_dates, "1:2", 15, 4, "line"),
    #     (COL.hol_notes, "3:3", 9, 3, "text"),
    #     (COL.donation, "1:4", 16, 0, "line"),
    #     (COL.barcode, "1:2", 16, 4, "line"),
    # ]

    settings.default_template = [
        ## non-algorithmic version needs to be: [title, (brick height, brick length), start-row, start-col]
        ## needs to be in same order as COL specification
        (COL.sublib, (1,2), 0, 0, "line"),
        (COL.langs, (1,2), 0, 2, "line"),
        (COL.isbn, (1,2), 0, 4, "line"),
        (COL.title, (2,3), 1, 0, "text"),
        (COL.tr_title, (2,3), 1, 3, "text"),
        (COL.subtitle, (2,3), 3, 0, "text"),
        (COL.tr_subtitle, (2,3), 3, 3, "text"),
        (COL.parallel_title, (2,3), 5, 0, "text"),
        (COL.tr_parallel_title, (2,3), 5, 3, "text"),
        (COL.parallel_subtitle, (2,3), 7, 0, "text"),
        (COL.tr_parallel_subtitle, (2,3), 7, 3, "text"),
        (COL.country_name, (1,2), 13, 0, "line"),
        (COL.state, (1,2), 13, 2, "line"),
        (COL.place, (1,2), 13, 4, "line"),
        (COL.publisher, (1,4), 14, 0, "line"),
        (COL.pub_year, (1,1), 14, 4, "line"),
        (COL.copyright, (1,1), 14, 5, "line"),
        (COL.extent, (1,1), 15, 1, "line"),
        (COL.size, (1,1), 15, 0, "line"),
        (COL.is_illustrated, (1,1), 15, 3, "checkbox"),
        (COL.series_title, (1,3), 12, 0, "line"),
        (COL.series_enum, (1,2), 12, 3, "line"),
        (COL.volume, (1,1), 12, 5, "line"),
        (COL.notes, (3,3), 9, 0, "text"),
        (COL.sales_code, (1,1), 15, 2, "line"),
        (COL.sale_dates, (1,2), 15, 4, "line"),
        (COL.hol_notes, (3,3), 9, 3, "text"),
        (COL.donation, (1,4), 16, 0, "line"),
        (COL.barcode, (1,2), 16, 4, "line"),
    ]
    settings.files.help_file = "html/help_art_cats.html"
    settings.files.output_dir = Path("your_marc_files")
    settings.files.full_output_dir = (
        settings.files.module_dir / settings.files.output_dir
    )
    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    CUSTOM_LOG_FILE = (
        # settings.files.full_output_dir / f"logger.{settings.timestamp}.log"
        settings.files.full_output_dir / "logger.log"
    )
    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
    form_gui.run(settings, COL)


if __name__ == "__main__":
    main()
