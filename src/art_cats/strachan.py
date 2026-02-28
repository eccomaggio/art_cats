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

# from . import marc_21

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

        langs = "language of resource"
        isbn = "ISBN"
        title = "Title"
        subtitle = "Subtitle"
        artist = "Artist"
        place = "(State,) City of publication"
        country_name = "Country of publication"
        publisher = "Publisher's name"
        pub_year = "Year of publication"
        copyright = "Year of copyright"
        pagination = "Pagination"
        size = "Size (height)"
        notes = "Note"
        authors = "Author(s)"
        call_number = "Call number"
        holding_note = "Holding note"
        barcode = "Barcode"

    ##### Tailor settings

    settings = Default_settings()
    settings.title = "strachan"
    settings.show_marc_button = True
    settings.headers = [member.display_title for member in COL]
    settings.show_table_view = True
    settings.locking_is_enabled = True
    settings.combos.data_file = "data/combo_data_artcats.yaml"
    settings.auto_submit_form_on_x_field = True
    settings.auto_submit_form_field_name = COL.barcode.name

    settings.validation.fields_to_clear = [
        COL.isbn,
        COL.title,
        COL.subtitle,
        COL.artist,
        COL.pagination,
        COL.pub_year,
        COL.notes,
        COL.copyright,
        COL.authors,
        COL.call_number,
        COL.holding_note,
        COL.barcode,
    ]

    settings.validation.fields_to_fill_info = {
        # COL.sublib.name : "ARTBL",
    }

    settings.validation.fields_to_fill = list(
        settings.validation.fields_to_fill_info.keys()
    )
    settings.validation.required_fields = [
        COL.langs.name,
        COL.title.name,
        COL.pub_year.name,
        COL.publisher.name,
        COL.country_name.name,
        COL.place.name,
        COL.pagination.name,
        COL.size.name,
        COL.barcode.name,
    ]

    settings.combos.independents = [
        # COL.is_illustrated.name,
    ]

    # settings.validation.validate_always = [COL.barcode.name]
    # settings.validation.validate_if_present = [COL.isbn.name]
    settings.validation.must_validate = [COL.barcode.name, COL.isbn.name]

    settings.validation.validation_skip_fieldname = COL.barcode.name

    settings.default_template = [
        ## non-algorithmic version needs to be:
        # [title,
        # (brick height, brick length),
        # start-row (0-indexed),
        # start-col]
        ## needs to be in same order as COL specification

        (COL.langs, (1, 2), 0, 0, "line"),
        (COL.isbn, (1, 2), 0, 2, "line"),
        (COL.title, (2, 3), 1, 0, "text"),
        (COL.subtitle, (2, 3), 1, 3, "text"),
        (COL.artist, (1, 2), 0, 4, "line"),
        (COL.place, (1, 3), 3, 0, "line"),
        (COL.country_name, (1, 3), 3, 3, "line"),
        (COL.publisher, (1, 2), 4, 0, "line"),
        (COL.pub_year, (1, 1), 4, 2, "line"),
        (COL.copyright, (1, 1), 4, 3, "line"),
        (COL.pagination, (1, 1), 4, 4, "line"),
        (COL.size, (1, 1), 4, 5, "line"),
        (COL.notes, (2, 2), 6, 0, "text"),
        (COL.authors, (1, 4), 5, 0, "line"),
        (COL.call_number, (1, 2), 5, 4, "line"),
        (COL.holding_note, (2, 2), 6, 2, "text"),
        (COL.barcode, (1, 2), 7, 4, "line"),
    ]

    settings.files.help_file = "html/help_art_cats.html"
    settings.files.output_dir = Path("your_marc_files")
    settings.files.full_output_dir = (
        settings.files.module_dir / settings.files.output_dir
    )

    if settings.create_output_dir:
        settings.files.full_output_dir.mkdir(exist_ok=True)

    CUSTOM_LOG_FILE = (
        settings.files.full_output_dir
        / "logger_strachan.log"
    )

    log_setup.setup_app_logging(log_file_path=CUSTOM_LOG_FILE)
    form_gui.run(settings, COL)


if __name__ == "__main__":
    main()
