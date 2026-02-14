from dataclasses import dataclass

from art_cats.settings import Default_settings
from . import validation

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


def gatekeeper(source: str, editor) -> None:
    """
        logic for gatekeepers:

        submit:
                check if dummy
                check if empty record
                check if empty file

                check for incomplete (validate)

        close:
                check for unsaved —> confirm
                check for incomplete (validate)

        update_current_position: (jump)
                check for unsaved —> confirm
                check for incomplete (validate)

        handle_clear_form: (clear)
                confirm action

        handle_create_new_record: (new)
                check for unsaved —> confirm
                check for incomplete (validate)

        handle_unlock: (lock)
                if about to lock:
                        check for unsaved —> confirm
                        check for incomplete (validate)

        handle_marc_files: (marc)
                check for unsaved —> confirm
                check for incomplete (validate)

        handle_create_new_file: (discard)
                check for unsaved —> confirm


    if dummy —> 		submit
    if empty record —> 	submit
    if empty file —> 	submit

    if incomplete —>	submit, close, update_pos, new record, unlock, marc,
    if unsaved info —>			close, update_pos, new record, unlock, marc, new file
    """
    print(f"gatekeeping for {source=}, {editor.data.all_text_is_saved=}")


def analyse_new_file(headers, col_enum):
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
