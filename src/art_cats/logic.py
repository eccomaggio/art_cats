from dataclasses import dataclass
from tkinter import W

from art_cats.settings import Default_settings
from . import validation
from . import io
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


def save_record_externally(editor) -> None:
    csv_file = io.get_csv_file_name_and_path(editor.settings)
    logger.info(f"{csv_file=}")
    editor.save_as_csv(csv_file)
    editor.update_nav_buttons()
    editor.load_record_into_gui(editor.data.current_row)


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
    x = ["a", "b", "c", "d", "e"]
    y = [1, 4, 2, 3, 0]
    z = map_list(x, y)
    assert z == ["e", "a", "c", "d", "b"]
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
        logger.warning("The mappings don't fit the list. (The mappings file is probably invalid or does not match the columns in the .csv)")
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
