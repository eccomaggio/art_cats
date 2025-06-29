from openpyxl import load_workbook
from dataclasses import dataclass
from typing import List
from enum import Enum, auto
from pprint import pprint
from datetime import datetime
# import datetime


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
    pub_year: str
    copyright: str
    extent:int
    size: int
    notes: str
    sales_code: str
    sale_dates: List[str]
    hol_note: str
    donation: str
    barcode: str
    pub_date_is_approx: bool
    extent_is_approx: bool
    timestamp: datetime

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


def get_records(excel_file):
    workbook = load_workbook(filename=excel_file)
    sheet = workbook.active
    print(f"\n{sheet.title} in {excel_file}")
    current_time = datetime.now()
    # standard_time = datetime.utcnow()
    # timestamp = str(standard_time).translate(str.maketrans("", "", " -:"))[:16]

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
            int(extent),
            normalize(value[17]),
            normalize(value[18]),
            normalize(value[19]),
            # *value[17:20],
            norm_dates(value[20]),
            normalize(value[21]),
            normalize(value[22]),
            normalize(value[23]),
            # *value[21:24],
            pub_date_is_approx,
            extent_is_approx,
            current_time,
            # timestamp,
        )
        # print(len(tmp))
        # records.append(Record(*tmp))
        records.append(record)
        record_type = devine_record_type(langs, bool(title_t), bool(p_title_t))
        print(f"**** {record_type}")
    return records

def normalize(entry):
    return str(entry).strip() if entry else None

def build_000():
    """leader (0 is only for sorting purposes; should read 'LDR')"""
    return (0, ["00000nam a22000003i 4500"])

def build_005(record):
    """date & time of transaction"""
    standard_time = record.timestamp.utcnow()
    # standard_time = datetime.now(datetime.UTC)
    timestamp = str(standard_time).translate(str.maketrans("", "", " -:"))[:16]
    return (5, [f"{timestamp}"])
    # return (5, [f"{record.timestamp}"])

def build_008(record):
    """pub year & main language?"""
    t = record.timestamp
    return (
        8,
        [
            f"{str(t.year)[2:]}{str(t.month).zfill(2)}{str(t.day).zfill(2)}s{record.pub_year}||||{record.place}||||||||||||||\\||eng||"
        ],
    )

def build_033(record):
    """sales dates"""
    count_of_dates = len(record.sale_dates)
    date_string = f"$a{"$a".join(record.sale_dates)}"
    return (33, [f"{count_of_dates}\\{date_string}"])

def build_040():
    """catalogued in Oxford"""
    return (40, ["\\\\$aUkOxU$beng$erda$cUkOxU"])

def build_245(record):
    """title"""
    return (245, ["TBA"])


def build_264(record):
    """publisher & copyright"""
    result = []
    place = f"$a {record.place}"
    publisher = f":$b {record.publisher}"
    pub_year = f",$c {record.pub_year}"
    result.append(f"\\0{place}{publisher}{pub_year}")

    if record.copyright:
        result.append(f"$a\u00a9 {record.copyright}")
    return (264, result)

def build_300(record):
    """physical description"""
    pages = f"{record.extent} pages"
    if record.extent_is_approx:
        pages = f"approximately {pages}"
    size = f"{record.size} cm"
    return (300, [f"\\$a{pages} ;$c{size}"])

def build_336():
    """content type (boilerplate)"""
    return (336, ["\\\\$atext$2rdacontent"])

def build_337():
    """media type (boilerplate)"""
    return (337, ["\\\\$aunmediated$2rdamedia"])

def build_338():
    """carrier type (boilerplate)"""
    return (338, ["\\\\$avolume$2rdacarrier"])

def build_876(record):
    """notes / donations / barcode"""
    notes = f"$z{record.notes}" if record.notes else ""
    # hol_note = f"$z{record.hol_note}" if record.hol_note else ""
    donation = f"$z{record.donation}" if record.donation else ""
    barcode = f"$p{record.barcode}"
    return (876, [f"\\\\{notes}{donation}{barcode}"])

def build_904():
    """authority (boilerplate)"""
    return (904, ["\\\\$aOxford Local Record"])

def build_024(record):	##optional
    """sales code (if exists)"""
    sales_code = f"8\\$a{record.sales_code.strip()}" if record.sales_code else ""
    return (24, [sales_code])

def build_041(record):	##optional
    """language codes if not monolingual"""
    lang_string = ""
    if len(record.lang) > 1:
        lang_string = f"\\0$a{"$a".join(record.lang)}"
    return (41, [lang_string])

def build_246(record):	##optional
    """Varying Form of Title"""
    result = "TBA" if record.p_title else ""
    return (246, [result])

def build_500(record):	##optional
    """general notes"""
    hol_note = f"\\\\$a{record.hol_note}" if record.hol_note else ""
    return (500, [hol_note])

def finesse_string(field):
    """transforms e.g.
    (40, ['blah']) -> (40, ['040=  blah'])
    """
    field_int = field[0]
    field_designator = str(field[0]).zfill(3) if field[0] else "LDR"
    field_contents = [f"{field_designator}=  {line}" for line in field[1]]
    return (field_int, field_contents)

def mark_nonfiling_words_in_titles(title):
    pass

def build_mark_records(records):
    mark_records = []
    for record in records:
        mark_record = []
        for boilerplate in (
            build_000,
            build_040,
            build_336,
            build_337,
            build_338,
            build_904,
        ):
            # print(boilerplate())
            mark_record.append(boilerplate())

        for step in (
            build_005,
            build_008,
            build_033,
            build_245,
            build_264,
            build_300,
            build_876,
            build_024,
            build_041,
            build_246,
            build_500,
        ):
            field = step(record)
            if len(field[1][0]):
                mark_record.append(field)
            # mark_record.append(field)

        mark_record.sort(key=lambda field: field[0])
        mark_record = [finesse_string(field) for field in mark_record]
        mark_records.append(mark_record)

    return mark_records


def main():
    # excel_file = "reviews-sample.xlsx"
    excel_file = "sample.xlsx"
    records = get_records(excel_file)
    mark_records = build_mark_records(records)

    # pprint(records)
    with open('test.mrk', 'w') as f:
        # f.write('readme')
        for record in mark_records:
            for field in record:
                for line in field[1]:
                    # print(line)
                    f.write(line)
                    f.write("\n")
            # print("")
            f.write("\n")
    # pprint(mark_records)


if __name__ == "__main__":
    main()
