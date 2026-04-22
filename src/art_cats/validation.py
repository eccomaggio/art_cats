from collections.abc import Callable

from art_cats import marc_21
from .settings import Default_settings
import logging
logger = logging.getLogger(__name__)


def validate(
        row_as_dict: dict[str, str],
        live_settings: Default_settings,
        optional_msg = ""
        ) -> tuple[list[str], str, bool]:
    ## TODO: tweak rules to fit art cats
    """
    goes through values in an excel row and checks their validity if required
    Args:
        row_as_dict (dict[str, str]) = {col_name: value}
        live_settings (Default_settings)
        optional_msg (str, optional): give optional context to errors

    Returns:
        1. a dummy marker
        (a dummy record is a trapdoor; it is not rendered into marc files)
        2. a list of the field names of problem items
        3. a text description of the problem details
    """
    # print(f"STUFF2: {optional_msg}")
    error_details = ""
    is_dummy = False
    problem_items = []
    missing = []
    invalid = []
    rules = live_settings.validation
    for col_num, (name, content) in enumerate(row_as_dict.items()):
        if is_a_dummy_record(name, content, rules):
            is_dummy = True
            break
            # continue
        if name in rules.required_fields and not content:
            missing.append(name)
            problem_items.append(name)
            continue
        if name in rules.must_validate:
            test = tests_by_fieldname[name]
            error_msg = test(name, content, row_as_dict)
            if error_msg:
                invalid.append(f"{name}: {error_msg}")
                problem_items.append(name)
    if not is_dummy:
        errors = []
        # if live_settings.title == "art_catalogue":
        if live_settings.show_marc_button:
            invalid, problem_items = validate_marc21_country_codes(row_as_dict, invalid, problem_items, col_num)
        if missing:
            count = len(missing)
            add_s = "s" if count > 1 else ""
            errors.append(
                f"The following {count} field{add_s} are missing: {', '.join(missing)}"
            )
        if invalid:
            count = len(invalid)
            add_s = "s" if count > 1 else ""
            errors.append(
                f"Please correct the {count} following problem{add_s}: {'; '.join(invalid)}"
            )
        if errors:
            error_details = "\n".join(errors)
            error_details = f"{optional_msg}{error_details}" if optional_msg else error_details
    return (problem_items, error_details, is_dummy)


## ** too early to check: records aren't coerced into data types until saving as marc
# def check_records_on_load(settings, column_names, rows) -> dict[int, tuple[list[str], str, bool]]|None:
#     """
#         Checks imported records are valid and produces a report of non-valid items
#         output: { row_num: ([problem columns], error_details, is_dummy)}
#     """
#     report:dict[int, tuple] = {}
#     print(f"DEBUG: {tests_by_fieldname}")
#     for row_num, row in enumerate(rows[1:]):    ## ignore 1st row (headers)
#         record_as_dict = {}
#         for col_num, value in enumerate(row):
#             name = column_names[col_num]
#             if row_num == 0:
#                 print(f"{row_num}: {name}->{value[:10]}")
#             record_as_dict[name] = value
#         row_report = validate(record_as_dict, settings)
#         if row_report[0]:
#             report[row_num] = row_report
#     if len(report):
#         logger.warning(f"Problems with imported data:\n{report}")
#     else:
#         logger.info("Imported data validates correctly.")
#     return report




def validate_marc21_country_codes(record_as_dict: dict, invalid: list, problem_items: list, row_num:int) -> tuple[list, list]:
    country = record_as_dict["country_name"]
    # state = record_as_dict["state"]
    place = record_as_dict["place"]
    country_code = marc_21.get_country_code(country, place, row_num)
    if country and not country_code:
        invalid.append(f"country of publication ({country}) is not recognized.")
        problem_items.append(country)
    return (invalid, problem_items)


def is_a_dummy_record(name:str, content:str, rules) -> bool:
    """
    NB must inject 'rules' as this file only has access to default settings
    """
    if (
        name == rules.validation_skip_fieldname
        and
        # content.lower().startswith(rules.validation_skip_text.lower())
        is_dummy_content(content, rules.validation_skip_text)
        ):
        return True
    else:
        return False


def is_a_dummy_record_by_index(index:int, content:str, target_index:int, dummy_content_marker:str) -> bool:
    # if index == target_index and content.lower().startswith(target_content.lower()):
    if index == target_index and is_dummy_content(content, dummy_content_marker):
        return True
    else:
        return False

def is_dummy_content(content:str, dummy_content_marker:str) -> bool:
    if content.lower().startswith(dummy_content_marker.lower()):
        return True
    else:
        return False


def university_id_number(name: str, content: str, record_as_dict={}) -> str:
    error_msg = ""
    if name and (
        len(name) != 7 or int(name[0]) in [1, 3, 6, 7]
    ):
        error_msg = f"'{name}' is not a valid University number."
    return error_msg


def isbn(name: str, content: str, record_as_dict={}) -> str:
    error_msg = ""
    if 10 > len(content) > 13:
        error_msg = "The ISBN is not valid."
    return error_msg


def barcode(name:str, content:str, record_as_dict={}) -> str:
    error_msg = ""
    errors = []
    if len(content) != 9:
        errors.append("have 9 digits")
    if content and content[0] not in "367":
        errors.append("start with 3, 6 or 7")
    error_count = len(errors)
    if error_count:
        if error_count == 2:
          error_msg = " and ".join(errors)
        else:
          error_msg = errors[0]
        error_msg = f"The barcode [{content}] must {error_msg}"
    return error_msg


# def languages(name:str, content:list[str], record_as_dict:dict) -> str:
#     ## ** Can't debug langs here because just a string, not a processed list
#     error_msg = ""
#     is_dual_language = record_as_dict.get("parallel_title", "") != ""
#     # print(f"DEBUG: langs={content}; {record_as_dict.get("parallel_title", "nowt")}")
#     if len(content) == 1 and is_dual_language:
#         error_msg = f"Parallel titles are only used with multi-language items but only one language is specified: {content[0]}"
#     return error_msg


tests_by_fieldname: dict[str, Callable] = {
    "hold_for" : university_id_number,
    "notify": university_id_number,
    "isbn": isbn,
    "barcode": barcode,
    # "langs" : languages,
}
