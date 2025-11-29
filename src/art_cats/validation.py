from collections.abc import Callable
from .settings import Default_settings
import logging
logger = logging.getLogger(__name__)


def validate(record_as_dict: dict[str, str], settings:Default_settings, optional_msg="") -> tuple[list[str], str]:
    ## TODO: check out optional_msg
    ## TODO: tweak rules to fit art cats
    """
    goes through values in a record and checks their validity if required
    Args:
        record_as_dict (dict[str, str])
        settings (Default_settings)
        optional_msg (str, optional): Not sure! Need to check!!. Defaults to "".

    Returns:
        None | tuple[list[str], str]: if empty, everything validated; otherwise return a list of the problematic field names and an error message containing the details
    """
    msg = ""
    missing = []
    invalid = []
    problem_items = []
    errors = []
    rules = settings.validation
    for name, content in record_as_dict.items():
        if is_a_dummy_record(name, content, rules):
            # return None
            continue
        if name in rules.required_fields and not content:
            missing.append(name)
            problem_items.append(name)
            continue
        if name in rules.must_validate:
            test = tests_by_name.get(name, None)
            if test:
                error_msg = test(name, content)
                if error_msg:
                    invalid.append(f"{name}: {error_msg}")
                    problem_items.append(name)
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
        msg = "\n".join(errors)

    # msg = "\n".join(errors)
    # if msg:
    #     return (problem_items, msg)
    # return ()
    return (problem_items, msg)


def is_a_dummy_record(name:str, content:str, rules) -> bool:
    if (
        name == rules.validation_skip_fieldname
        and
        # content.lower().startswith(rules.validation_skip_text.lower())
        is_dummy_content(content, rules.validation_skip_text)
        ):
        return True
    else:
        return False


def is_a_dummy_record_by_index(index:int, content:str, target_index:int, target_content:str) -> bool:
    # if index == target_index and content.lower().startswith(target_content.lower()):
    if index == target_index and is_dummy_content(content, target_content):
        return True
    else:
        return False

def is_dummy_content(content:str, target_content:str) -> bool:
    if content.lower().startswith(target_content.lower()):
        return True
    else:
        return False


def university_id_number(name: str, content: str) -> str:
    error_msg = ""
    if name and (
        len(name) != 7 or int(name[0]) in [1, 3, 6, 7]
    ):
        error_msg = "This is not a valid University number."
    return error_msg


def isbn(name: str, content: str) -> str:
    error_msg = ""
    if 10 > len(content) > 13:
        error_msg = "The ISBN is not valid."
    return error_msg


def barcode(name:str, content:str) -> str:
    error_msg = ""
    if len(content) != 9:
        error_msg = "A barcode must have 9 digits"
    if content[0] not in "367":
        error_msg = "A barcode needs to start with 3, 6 or 7"
    return error_msg


tests_by_name: dict[str, Callable] = {
    "hold_for" : university_id_number,
    "notify": university_id_number,
    "isbn": isbn,
    "barcode": barcode,
}
