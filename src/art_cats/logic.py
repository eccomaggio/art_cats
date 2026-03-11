from dataclasses import dataclass, fields

# from tkinter import W
from pathlib import Path

from art_cats.settings import Default_settings
from . import validation
from . import io
from . import marc_21
import logging

logger = logging.getLogger(__name__)


@dataclass
class Data:
    excel_rows = [[]]
    headers = []
    has_records = False
    file_name = ""
    current_row_index = 0
    record_is_locked = False
    all_text_is_saved = True
    # record_is_new = True

    @property
    def row_count(self) -> int:
        return len(self.excel_rows)

    @property
    def column_count(self) -> int:
        return len(self.excel_rows[0])

    @property
    def current_record_is_new(self) -> int:
        return self.current_row_index == -1

    @property
    def record_count(self) -> int:
        return len(self.excel_rows)

    @property
    def index_of_last_record(self) -> int:
        return self.record_count - 1

    @property
    def current_row(self) -> list:
        return self.excel_rows[self.current_row_index]

    @current_row.setter
    def current_row(self, row: list) -> None:
        self.excel_rows[self.current_row_index] = row


def gatekeeper(source: str, editor) -> bool:
    """
    *LOGIC:

    This routine is called whenever a record is saved or
    data could be lost because a record is unsaved when
    a user moves on to the next record.

    *Assumptions:
    if a record is saved:
        assume it is valid
        no need to save again
    else:
        submit -> validate & save
        other -> abort and prompt to repair & try again

    *identifiers:
    These are passed to the routine by the caller:
            submit -> handle_submit()
            close -> handle_close()
            jump -> update_current_position()
            clear -> handle_clear_form()
            new -> handle_create_new_record()
            lock -> handle_unlock()
            marc -> handle_marc_files()
            discard -> handle_create_new_file()
            barcode -> choose_to_save_on_barcode()
    """
    authorised_to_continue = False

    is_saved = check_if_saved(editor, source)
    # print(f"gatekeeping for {source=} [{is_saved=}]")
    if source not in ["submit"]:
        if is_saved:
            authorised_to_continue = True
        else:
            authorised_to_continue = False
            editor.show_alert_box(
                "Check the record is correct and then save it before continuing."
            )
    else:
        if is_saved:
            authorised_to_continue = False
        else:
            authorised_to_continue = check_record_can_be_saved(editor)
    return authorised_to_continue


def check_record_can_be_saved(editor, source="submit") -> bool:
    record_as_dict, is_empty = editor.get_all_inputs()
    if is_empty:
        authorised_to_continue = handle_empty_records(editor, source)
    else:
        problem_items, error_details, is_dummy = validation.validate(
            record_as_dict,
            editor.settings,
        )
        if problem_items:
            editor.highlight_fields(problem_items)
            editor.show_alert_box(error_details)
            authorised_to_continue = False
        else:
            add_record(editor, record_as_dict)
            authorised_to_continue = True
    return authorised_to_continue


def check_if_saved(editor, source) -> bool:
    """
    Checks whether there is unsaved text in the record.
    This is normal for a submit-record request, but if
    if is for some other operation, **the user is given
    the option to abort**.
    """
    # return not editor.data.all_text_is_saved
    record_is_saved = editor.data.all_text_is_saved
    if not record_is_saved and source not in ("submit", "lock"):
        record_is_saved = not editor.choose_to_abort_on_unsaved_text()
    # treat_as_saved = False
    # if source != "submit" and not editor.data.all_text_is_saved:
    #     treat_as_saved = not editor.choose_to_abort_on_unsaved_text()
    #     # all_saved = False
    #     # error_msg = "There is some unsaved information. Please save before continuing"
    #     # editor.show_alert_box(error_msg)
    return record_is_saved


def handle_empty_records(editor, source: str) -> bool:
    if source in ("discard"):
        save_is_authorised = True
    elif editor.data.current_record_is_new:
        editor.show_alert_box(
            "There is no information to save. You can either enter a record or simply close the app."
        )
        # return False
        save_is_authorised = False
    else:
        editor.delete_record()
        # return True
        save_is_authorised = True
    return save_is_authorised


def add_record(editor, record_as_dict) -> None:
    record_as_data_row = list(record_as_dict.values())
    # print("OK... data passes as valid for submission...")
    if editor.data.current_record_is_new:
        # print(f"***{self.has_records=}, record count: {self.record_count} {data=}")
        if editor.data.has_records:
            editor.data.excel_rows.append(record_as_data_row)
        else:
            editor.data.excel_rows = [record_as_data_row]
            editor.data.has_records = True
        editor.data.current_row_index = editor.data.index_of_last_record
        editor.update_title_with_record_number()
    else:
        ## Update existing record
        editor.data.current_row = record_as_data_row


# def save_record_externally(editor) -> None:
#     csv_file = io.get_csv_file_name_and_path(editor.settings)
#     logger.info(f"{csv_file=}")
#     editor.save_as_csv(csv_file)
#     editor.update_nav_buttons()
#     editor.load_record_into_gui(editor.data.current_row)


def delete_record(editor, index=-1) -> None:
    if index == -1:
        index = editor.data.current_row_index
    del editor.data.excel_rows[index]
    index_of_last_record = editor.data.index_of_last_record
    if index > index_of_last_record:
        index = index_of_last_record
        editor.data.current_row_index = index_of_last_record
    # print(f"????? {index=}")
    if editor.data.record_count:
        editor.load_record_into_gui(editor.data.excel_rows[index])


def is_expected_filetype(headers, col_enum):
    expected_col_count = len(col_enum)
    file_resembles_expectations = len(headers) == expected_col_count
    # print(f">>> >> > {expected_col_count=}: {len(headers)=} -> {file_resembles_expectations=}")
    return file_resembles_expectations


def get_human_readable_record_number(current_row_index, number=-100):
    if number == -100:
        number = current_row_index
    if number == -1:
        out = "[new]"
    else:
        out = str(number + 1)
    return out


def map_list(orig: list, mappings: list) -> list:
    """
    'new' is returned where each of its elements
    come from 'orig'
    but moved to the index specified in 'mappings'
    TEST:
    csv_cols = ["a", "b", "c", "d", "e"]
    mappings = [1, 4, 2, 3, 0]
    remapped_cols  = map_list(csv_cols, mappings)
    assert remapped_cols == ["e", "a", "c", "d", "b"]
    """
    if not map_fits_list(mappings, orig):
        return orig
    new = ["" for _ in mappings]
    for pos, value in enumerate(orig):
        new_pos = mappings[pos]
        new[new_pos] = value
        # print(f"{value} @ {pos} -> {new_pos}: {new}")
    return new


def unmap_list(mapped: list, mappings: list) -> list:
    """
    'mapped' is a list  constructed from 'mappings'
    'orig' returns the elements in their original order
    before 'mappings' was applied
    """
    if not map_fits_list(mappings, mapped):
        return mapped
    orig = ["" for _ in mappings]
    for orig_pos, mapped_pos in enumerate(mappings):
        value = mapped[mapped_pos]
        orig[orig_pos] = value
        # print(f"{value} @ {pos} -> {new_pos}: {new}")
    return orig


def map_fits_list(mappings: list, orig: list) -> bool:
    result = True
    if len(orig) != len(mappings):
        result = False
    else:
        test1 = sorted(mappings)
        test2 = list(range(test1[0], test1[-1] + 1))
        if test1 != test2:
            result = False
    if not result:
        logger.warning(
            "The mappings don't fit the list. (The mappings file is probably invalid or does not match the columns in the .csv)"
        )
    return result


# def map_fits_list(mappings: list, orig: list) -> bool:
#     """
#     * orig & mappings must be equal length
#     * elements in mappings must be contiguous when sorted
#     """
#     if len(orig) != len(mappings):
#         return False
#     test1 = sorted(mappings)
#     test2 = list(range(test1[0], test1[-1] + 1))
#     if test1 != test2:
#         return False
#     return True


def format_list_for_marc(
    records: list[list[str]], live_settings: Default_settings
) -> list[list[str]]:
    internal_fields = {
        "state",
        "country_code",
        "pub_year_is_approx",
        "pagination_is_approx",
        "timestamp",
        "sequence_number",
        "links",
    }
    marc_column_names = [
        f.name for f in fields(marc_21.Record) if f.name not in internal_fields
    ]
    augmented_records = []
    must_normalise_column_order = bool(live_settings.csv_to_marc_mappings)
    if must_normalise_column_order:
        logger.info("Normalising columns to match expected order.")
    for record_num, record in enumerate(records):
        # * apply corrective column mapping if necessary
        if must_normalise_column_order:
            record = map_list(record, live_settings.csv_to_marc_mappings)
        # else:
        #     record = raw_record
        curr_row = []
        _col = iter(record)
        # print(f"Record number {record_num + 1}:")
        for i, marc_col_name in enumerate(marc_column_names):
            if marc_col_name in live_settings.column_names:
                contents = next(_col)
            else:
                contents = ""
            # print(f"\t{i} {marc_col_name}: {contents=}")
            curr_row.append(contents)
        augmented_records.append(curr_row)

    # print("** format list for marc:")
    # print(f"{len(augmented_records[1])}->{augmented_records[1]}")
    # print(f"{len(marc_column_names)}->{marc_column_names}\n")
    return augmented_records


def remove_dummy_records(
    records: list[list[str]], live_settings: Default_settings, COL
) -> list:
    target_col_name = live_settings.validation.validation_skip_fieldname
    if not target_col_name:
        return records
    # print(f">>>>>>>>>>>>>{target_col_name}")
    target_col_index = COL[target_col_name].value
    list_without_dummies = []
    indices_of_dummies = []
    for i, record in enumerate(records):
        is_dummy = validation.is_dummy_content(
            record[target_col_index], live_settings.validation.validation_skip_text
        )
        if is_dummy:
            indices_of_dummies.append(i)
            # continue
        else:
            list_without_dummies.append(record)
    # print(f">>>> {len(records)=} vs {len(list_without_dummies)=}")
    # number_of_records_removed = len(records) - len(list_without_dummies)
    number_of_records_removed = len(indices_of_dummies)
    # if number_of_records_removed > 0:
    if number_of_records_removed > 0:
        print(f"{indices_of_dummies=}")
        logging.warning(
            f"The following {number_of_records_removed} dummy record{singular_or_plural(number_of_records_removed)} {singular_or_plural(number_of_records_removed, "were", "was")} removed from the export to Marc 21 format: {", ".join((str(el + 1) for el in indices_of_dummies))}"
        )
    return list_without_dummies


def singular_or_plural(count: int, plural="s", singular="") -> str:
    return plural if count != 1 else singular


known_patterns = {
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
        ],
    ],
    "strachan": [
        [
            ("langs", (1, 2), 0, 0, "line"),
            ("isbn", (1, 2), 0, 2, "line"),
            ("title", (2, 3), 1, 0, "text"),
            ("subtitle", (2, 3), 1, 3, "text"),
            ("artist", (1, 2), 0, 4, "line"),
            ("place", (1, 3), 3, 0, "line"),
            ("country_name", (1, 3), 3, 3, "line"),
            ("publisher", (1, 2), 4, 0, "line"),
            ("pub_year", (1, 1), 4, 2, "line"),
            ("copyright", (1, 1), 4, 3, "line"),
            ("pagination", (1, 1), 4, 4, "line"),
            ("size", (1, 1), 4, 5, "line"),
            ("notes", (2, 2), 6, 0, "text"),
            ("authors", (1, 4), 5, 0, "line"),
            ("call_number", (1, 2), 5, 4, "line"),
            ("hol_notes", (2, 2), 6, 2, "text"),
            ("barcode", (1, 2), 7, 4, "line"),
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
            "Barcode",
        ],
    ],
    "orders": [
        [
            ("subject_consultant", (1, 2), 0, 0, "combo"),
            ("fund_code", (1, 2), 1, 0, "combo"),
            ("order_type", (1, 2), 2, 0, "combo"),
            ("bib_info", (2, 6), 3, 0, "text"),
            ("creator", (1, 2), 7, 0, "line"),
            ("date", (1, 2), 7, 2, "line"),
            ("isbn", (1, 2), 7, 4, "line"),
            ("library", (1, 2), 0, 2, "combo"),
            ("location", (1, 2), 1, 2, "combo"),
            ("item_policy", (1, 2), 2, 2, "combo"),
            ("reporting_code_1", (1, 2), 0, 4, "combo"),
            ("reporting_code_2", (1, 2), 1, 4, "combo"),
            ("reporting_code_3", (1, 2), 2, 4, "combo"),
            ("hold_for", (1, 2), 8, 0, "line"),
            ("notify", (1, 2), 9, 0, "line"),
            ("additional_info", (2, 4), 8, 2, "text"),
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


def update_settings(settings, COL, pattern_name: str) -> None:
    match pattern_name:
        case "art_cats":
            settings.title = pattern_name
            settings.show_marc_button = True
            # settings.column_names = [column.name for column in COL]
            # settings.headers = [member.display_title for member in COL]
            settings.show_table_view = False
            settings.locking_is_enabled = True
            settings.combos.data_file = "data/combo_data_artcats.yaml"
            settings.auto_submit_form_on_x_field = True
            settings.auto_submit_form_field_name = COL.barcode.name
            settings.validation.fields_to_clear = [
                COL.barcode,
                # COL.hol_notes,  # temporarily contains 'item policy'
                COL.pagination,
                COL.pub_year,
                COL.sale_dates,
                COL.copyright,
                COL.sale_dates,
                COL.sales_code,
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
                # COL.extent.name,
                COL.pub_year.name,
                COL.publisher.name,
                COL.country_name.name,
                COL.place.name,
                COL.pagination.name,
                COL.size.name,
                COL.barcode.name,
                COL.illustrations,
            ]
            settings.combos.independents = [
                COL.illustrations.name,
            ]
            settings.validation.must_validate = [COL.barcode.name, COL.isbn.name]
            settings.validation.validation_skip_fieldname = COL.barcode.name
            settings.files.help_file = "html/help_art_cats.html"
            settings.files.output_dir = Path("your_marc_files")
            settings.files.full_output_dir = (
                settings.files.module_dir / settings.files.output_dir
            )

        case "strachan":
            settings.title = "strachan"
            settings.show_marc_button = True
            # settings.column_names = [column.name for column in COL]
            # settings.headers = [member.display_title for member in COL]
            settings.csv_to_marc_mappings = [
                0,
                1,
                2,
                3,
                15,
                5,
                4,
                6,
                7,
                8,
                9,
                10,
                11,
                14,
                16,
                12,
                13,
            ]
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
                COL.hol_notes,
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
            settings.validation.must_validate = [COL.barcode.name, COL.isbn.name]
            settings.validation.validation_skip_fieldname = COL.barcode.name
            settings.files.help_file = "html/help_art_cats.html"
            settings.files.output_dir = Path("your_marc_files")
            settings.files.full_output_dir = (
                settings.files.module_dir / settings.files.output_dir
            )

        case "orders":
            settings.title = pattern_name
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
            settings.files.help_file = "html/help_order_form.html"
            settings.files.output_dir = Path("your_order")
            settings.files.full_output_dir = (
                settings.files.module_dir / settings.files.output_dir
            )

        case "default":
            ## TODO: delete settings below and keep them in settings.py??
            settings.title = pattern_name
            settings.show_table_view = True
            settings.locking_is_enabled = False
            settings.use_default_layout = False
            settings.validation.fields_to_clear = [
                # COL.isbn,
            ]

            settings.validation.required_fields = [
                # COL.subject_consultant.name,
            ]

            settings.validation.must_validate = [
                # COL.isbn.name,
            ]

            settings.combos.independents = [
                # COL.subject_consultant.name,
            ]

            settings.files.full_output_dir = (
                settings.files.module_dir / settings.files.output_dir
            )

        case _:
            # logging.warning()
            print(f"{pattern_name} is not a recognised filetype.")
