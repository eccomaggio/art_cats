from openpyxl import load_workbook
from dataclasses import dataclass
from typing import List
from enum import Enum, auto
from pprint import pprint


@dataclass
class Record:
    sublib: str
    lang: List[str]
    isbn: str
    title: str
    title_t: str
    subtitle: str
    subtitle_t: str
    p_title: str
    p_title_t: str
    p_subtitle: str
    p_subtitle_t: str
    country: str
    place: str
    publisher: str
    pub_date: str
    copyright: str
    extent:int
    size: int
    notes: str
    sales_code: str
    sale_date: List[str]
    hol_note: str
    donation: str
    barcode: str
    pub_date_is_approx: bool
    extent_is_approx: bool

class Record_type(Enum):
    unknown = auto()
    english_only = auto()
    chinese_only = auto()
    english_primary = auto()
    chinese_primary = auto()



def norm_langs(raw):
    lang_list = { "english": "eng", "chinese": "chi", }
    result = [lang_list[lang.strip().lower()] for lang in raw.split("/")]
    # print(f"**{raw} -> {result}")
    return result

def norm_dates(raw):
    result = [date.strip() for date in raw.split(",")  ]
    # print(f"**{raw} -> {result}")
    return result

# def norm_pub_date(raw):
#     return check_for_approx(raw)

# def norm_extent(raw):
# return check_for_approx(raw)

def check_for_approx(raw):
    raw = raw.strip()
    is_approx = False
    if (raw[-1] == "?"):
        is_approx = True
        raw = raw[:-1]
    return (raw, is_approx)

def devine_record_type(langs, has_title_t, has_ptitle_t):
    language_count = len(langs)
    if (language_count == 1):
        record_type = Record_type.chinese_only if (has_title_t) else Record_type.english_only
    elif (language_count == 2):
        record_type = Record_type.chinese_primary if (has_title_t) else Record_type.english_primary
    else:
        record_type = Record_type.unknown
    return record_type


def main():
    # excel_file = "reviews-sample.xlsx"
    excel_file = "sample.xlsx"
    workbook = load_workbook(filename=excel_file)
    sheet = workbook.active
    print(f"\n{sheet.title} in {excel_file}")

    records = []

    # for value in sheet.iter_rows(min_row=2, max_row=2, values_only=True):
    for value in sheet.iter_rows(min_row=2, values_only=True):
        if (not value[0]):
            break

        langs = norm_langs(value[1])
        pub_date, pub_date_is_approx = check_for_approx(value[14])
        extent, extent_is_approx = check_for_approx(value[16])
        title_t = value[4]
        p_title_t = value[8]

        record = Record(
            value[0],
            langs,
            *value[2:14],
            pub_date,
            value[15],
            extent,
            *value[17:20],
            norm_dates(value[20]),
            *value[21:24],
            pub_date_is_approx,
            extent_is_approx,
        )
        # print(len(tmp))
        # records.append(Record(*tmp))
        records.append(record)
        record_type = devine_record_type(langs, bool(title_t), bool(p_title_t))
        print(f"**** {record_type}")
    pprint(records)


if __name__ == "__main__":
    main()
