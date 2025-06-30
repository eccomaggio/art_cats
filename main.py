from openpyxl import load_workbook
from dataclasses import dataclass
from typing import List
from enum import Enum, auto
from pprint import pprint
from datetime import datetime, timezone

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
    extent: int
    size: int
    notes: str
    sales_code: str
    sale_dates: List[str]
    hol_note: str
    donation: str
    barcode: str
    pub_year_is_approx: bool
    extent_is_approx: bool
    timestamp: datetime


def norm_langs(raw):
    lang_list = {
        "english": "eng",
        "chinese": "chi",
    }
    result = [lang_list[lang.strip().lower()] for lang in raw.split("/")]
    return result


def norm_dates(raw):
    result = [date.strip() for date in raw.split(",")]
    return result


def normalize(entry):
    return str(entry).strip() if entry else None


def check_for_approx(raw):
    raw = raw.strip()
    is_approx = False
    if raw[-1] == "?":
        is_approx = True
        raw = raw[:-1]
    return (raw, is_approx)


def get_records(excel_file):
    workbook = load_workbook(filename=excel_file)
    sheet = workbook.active
    print(f"\n{sheet.title} in {excel_file}")
    current_time = datetime.now()
    records = []
    for value in sheet.iter_rows(min_row=2, values_only=True):
        if not value[0]:
            break
        langs = norm_langs(value[1])
        pub_date, pub_date_is_approx = check_for_approx(str(value[14]))
        extent, extent_is_approx = check_for_approx(value[16])
        record = Record(
            value[0],
            langs,
            normalize(value[2]),
            normalize(value[3]),
            normalize(value[4]),
            normalize(value[5]),
            normalize(value[6]),
            normalize(value[7]),
            normalize(value[8]),
            normalize(value[9]),
            normalize(value[10]),
            normalize(value[11]),
            normalize(value[12]),
            normalize(value[13]),
            pub_date,
            normalize(value[15]),
            int(extent),
            normalize(value[17]),
            normalize(value[18]),
            normalize(value[19]),
            norm_dates(value[20]),
            normalize(value[21]),
            normalize(value[22]),
            normalize(value[23]),
            pub_date_is_approx,
            extent_is_approx,
            current_time,
        )
        records.append(record)
    return records


def build_000():
    """leader (0 is only for sorting purposes; should read 'LDR')"""
    return build_field(0, [[-2,-2,"00000nam a22000003i 4500"]])


def build_005(record):
    """date & time of transaction"""
    standard_time = record.timestamp.now(timezone.utc)
    timestamp = str(standard_time).translate(str.maketrans("", "", " -:"))[:16]
    return build_field(5, [[-2, -2, f"{timestamp}"]])


def build_008(record):
    """pub year & main language?"""
    t = record.timestamp
    return build_field( 8, [[-2,-2, f"{str(t.year)[2:]}{str(t.month).zfill(2)}{str(t.day).zfill(2)}s{record.pub_year}{4*"|"}{record.place}{14*"|"}\\||eng||" ]])


def build_033(record):
    """sales dates"""
    count_of_dates = len(record.sale_dates)
    date_string = f"$a{"$a".join(record.sale_dates)}"
    return build_field(33, [[count_of_dates,-1, date_string]])


def build_040():
    """catalogued in Oxford"""
    return build_field(40, [[-1,-1,"$aUkOxU$beng$erda$cUkOxU"]])


def build_245(record):
    """
    Title
    """
    has_chinese_title = bool(record.title_t)
    if has_chinese_title:
        title, subtitle = record.title_t, record.subtitle_t
        nonfiling = 0
    else:
        title, subtitle = record.title, record.subtitle
        nonfiling, title = mark_nonfiling_words(title)
    title = combine(title, subtitle)
    return build_field(245, [[0,nonfiling, f"$a{title}"]])


def build_264(record):
    """publisher & copyright"""
    result = []
    place = f"$a {record.place}"
    publisher = f":$b {record.publisher}"
    pub_year = record.pub_year
    if record.pub_year_is_approx:
        pub_year = f"[{pub_year}?]"
    pub_year = f",$c {pub_year}"
    result.append([-1, 0, f"{place}{publisher}{pub_year}"])

    if record.copyright:
        result.append([-2,-2,f"$a\u00a9 {record.copyright}"])
    return build_field(264, result)


def build_300(record):
    """physical description"""
    pages = f"{record.extent} pages"
    if record.extent_is_approx:
        pages = f"approximately {pages}"
    size = f"{record.size} cm"
    return build_field(300, [[-1, -2, f"$a{pages} ;$c{size}"]])


def build_336():
    """content type (boilerplate)"""
    return build_field(336, [[-1, -1, "$atext$2rdacontent"]])


def build_337():
    """media type (boilerplate)"""
    return build_field(337, [[-1, -1, "$aunmediated$2rdamedia"]])


def build_338():
    """carrier type (boilerplate)"""
    return build_field(338, [[-1, -1, "$avolume$2rdacarrier"]])


def build_876(record):
    """notes / donations / barcode"""
    notes = f"$z{record.notes}" if record.notes else ""
    donation = f"$z{record.donation}" if record.donation else ""
    barcode = f"$p{record.barcode}"
    return build_field(876, [[-1, -1, f"{notes}{donation}{barcode}"]])


def build_904():
    """authority (boilerplate)"""
    return build_field(904, [[-1, -1, "$aOxford Local Record"]])


def build_024(record):  ##optional
    """sales code (if exists)"""
    result = (
        build_field(24, [[8, -1, f"$a{record.sales_code.strip()}"]])
        if record.sales_code
        else ""
    )
    return result


def build_041(record):  ##optional
    """language codes if not monolingual"""
    is_multi_lingual = len(record.lang) > 1
    result = (
        build_field(41, [[-1, 0, f"$a{"$a".join(record.lang)}"]])
        if is_multi_lingual
        else ""
    )
    return result


def build_246(record):  ##optional
    """
    Varying Form of Title
    Holds parallel Western title AND/OR original Chinese character title
    """
    result = ""
    has_parallel_title = bool(record.p_title)
    has_chinese_main_title = bool(record.title_t)
    has_chinese_parallel_title = bool(record.p_title_t)

    ## Deal with original Chinese character titles
    if has_chinese_main_title:
        chinese_character_title = combine(record.title, record.subtitle)
    else:
        chinese_character_title = ""

    ## Deal with parallel titles (Parallel titles are only for dual-language catalogues)
    nonfiling = 0
    if has_chinese_parallel_title:
        parallel_title = combine(record.p_title_t, record.p_title)
        parallel_subtitle = combine(record.p_subtitle_t, record.p_subtitle)
        nonfiling = 0
    elif has_parallel_title:  ## (i.e. Western script)
        parallel_title, parallel_subtitle = record.p_title, record.p_subtitle
        nonfiling, parallel_title = mark_nonfiling_words(parallel_title)
    else:
        parallel_title = ""
    if parallel_title:
        parallel_title = combine(parallel_title, parallel_subtitle)

    ## Combine Chinese character main title with Western parallel title (if either exists)
    ## (not sure how to handle Chinese original title + parallel titles)
    if has_chinese_main_title:
        result = combine(chinese_character_title, parallel_title)
    else:
        result = parallel_title

    result = build_field(246, [[0, nonfiling, f"$a{result}"]]) if result else ""
    return result


def build_500(record):  ##optional
    """general notes"""
    result = (
        build_field(500, [[-1, -1, f"$a{record.hol_note}"]]) if record.hol_note else ""
    )
    return result


def build_field(numeric_tag, data):
    if data:
        lines = []
        display_tag = "LDR" if numeric_tag == 0 else str(numeric_tag).zfill(3)
        line_start = f"{display_tag}=  "
        for line in data:
            i1 = expand_indicators(line[0])
            i2 = expand_indicators(line[1])
            lines.append(f"{line_start}{i1}{i2}{line[2]}")
        result = (numeric_tag, lines)
    else:
        result = ""
    return result


def expand_indicators(indicator):
    expansions = {-2: "", -1: "\\"}
    return expansions.get(indicator, indicator)


def mark_nonfiling_words(title):
    nonfiling = 0
    if title:
        test = title.split("@@")
        if len(test) > 1:
            nonfiling = len(test[0])
            title = test[0] + test[1]
    return (nonfiling, title)


def combine(title, subtitle, sep="$b"):
    if subtitle:
        title += sep + subtitle
    return title


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
            if field:
                mark_record.append(field)

        mark_record.sort(key=lambda field: field[0])
        mark_records.append(mark_record)

    return mark_records


def main():
    # excel_file = "reviews-sample.xlsx"
    excel_file = "sample.xlsx"
    records = get_records(excel_file)
    mark_records = build_mark_records(records)

    with open("output.mrk", "w") as f:
        for record in mark_records:
            for field in record:
                for line in field[1]:
                    # print(line)
                    f.write(line)
                    f.write("\n")
            f.write("\n")
    # pprint(records)


if __name__ == "__main__":
    main()
