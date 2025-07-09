from openpyxl import load_workbook
from dataclasses import dataclass
from collections import namedtuple
from typing import List
from enum import Enum, auto
# from pprint import pprint
from datetime import datetime, timezone
import re
from pathlib import Path
# import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="output.log",
    filemode="w",
    encoding="utf-8",
    format="%(levelname)s:%(message)s",
    level=logging.DEBUG
    )
# logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


@dataclass
class Title:
    original: str
    transliteration: str


@dataclass
class Record:
    sublib: str
    langs: List[str]
    isbn: str
    title: Title
    subtitle: Title
    parallel_title: Title
    parallel_subtitle: Title
    country: str
    place: str
    publisher: str
    pub_year: str
    copyright: str
    extent: str
    size: int
    series_title: str
    series_enum: str
    notes: str
    sales_code: str
    sale_dates: List[str]
    hol_notes: str
    donation: str
    barcode: str
    pub_year_is_approx: bool
    extent_is_approx: bool
    timestamp: datetime
    sequence_number: int
    links: List


class MissingFieldError(Exception):
    pass


optional_fields = [
    24,     ## sales code
    41,     ## language if not monolingual
    246,    ## parallel title
    490,    ## series statement
    500,    ## general notes
    880,    ## transliteration
    ]


def norm_langs(raw):
    lang_list = {
        "english": "eng",
        "chinese": "chi",
        "german": "ger",
        "italian": "ita",
        "spanish": "spa",
        "french": "fre",
        "swedish": "swe",
        "danish": "dan",
        "norwegian": "nor",
        "dutch": "dut",
    }
    result = []
    langs = raw.replace(" ", "").lower().split("/")
    for lang in langs:
        try:
            result.append(lang_list[lang])
        except KeyError as e:
            logger.warning(f"Warning: {e} is not a recognised language; it has been passed on unchanged.")
            result.append(lang)
    # result = [lang_list[lang.strip().lower()] for lang in raw.split("/")]
    return result


def norm_country(country):
    # countries = {
    #     "china": "cc",
    #     "australia": "at",
    #     "newzealand": "nz",
    #     "france": "fr",
    #     "germany": "gw",
    #     "italy": "it",
    #     "portugal": "po",
    #     "netherlands": "ne",
    #     "spain": "sp",
    #     "sweden": "sw",
    #     "denmark": "dk",
    #     "norway": "no",
    #     "uk": "xxk",
    #     # "newyork": "nyu",
    #     # "england": "enk",
    #     # "northernireland": "nik",
    #     # "scotland": "stk",
    #     # "wales": "wlk",
    #     "canada": "xxc",
    #     "us": "xxu",
    #     "usa": "xxu",
    #     "austria": "au",
    #     "switzerland": "sz",
    #     "sanmarino": "sm",
    #     "montecarlo": "mc"
    # }

    countries = {
        "algeria": "ae",
        "angola": "ao",
        "benin": "dm",
        "botswana": "bs",
        "burkinafaso": "uv",
        "burundi": "bd",
        "cameroon": "cm",
        "centralafricanrepublic": "cx",
        "chad": "cd",
        "congo": "cf",
        "democraticrepublicofcongo": "cg",
        "côtedivoire": "iv",
        "cotedivoire": "iv",
        "djibouti": "ft",
        "egypt": "ua",
        "equatorialguinea": "eg",
        "eritrea": "ea",
        "ethiopia": "et",
        "gabon": "go",
        "gambia": "gm",
        "ghana": "gh",
        "guinea": "gv",
        "guineabissau": "pg",
        "kenya": "ke",
        "lesotho": "lo",
        "liberia": "lb",
        "libya": "ly",
        "madagascar": "mg",
        "malawi": "mw",
        "mali": "ml",
        "mauritania": "mu",
        "morocco": "mr",
        "mozambique": "mz",
        "namibia": "sx",
        "niger": "ng",
        "nigeria": "nr",
        "rwanda": "rw",
        "saotomeandprincipe": "sf",
        "senegal": "sg",
        "sierraleone": "sl",
        "somalia": "so",
        "southafrica": "sa",
        "southsudan": "sd",
        "spanishnorthafrica": "sh",
        "sudan": "sj",
        "swaziland": "sq",
        "tanzania": "tz",
        "togo": "tg",
        "tunisia": "ti",
        "uganda": "ug",
        "westernsahara": "ss",
        "zambia": "za",
        "zimbabwe": "rh",
        "afghanistan": "af",
        "armenia": "ai",
        "republicofarmenia": "ar",
        "azerbaijan": "aj",
        "bahrain": "ba",
        "bangladesh": "bg",
        "bhutan": "bt",
        "brunei": "bx",
        "burma": "br",
        "cambodia": "cb",
        "china": "cc",
        "cyprus": "cy",
        "easttimor": "em",
        "gazastrip": "gz",
        "georgia": "gs",
        "georgianrepublic": "gs",
        "republicofgeorgia": "gs",
        "india": "ii",
        "indonesia": "io",
        "iran": "ir",
        "iraq": "iq",
        "israel": "is",
        "japan": "ja",
        "jordan": "jo",
        "kazakhstan": "kz",
        "northkorea": "kn",
        "korea": "ko",
        "southkorea": "ko",
        "kuwait": "ku",
        "kyrgyzstan": "kg",
        "laos": "ls",
        "lebanon": "le",
        "malaysia": "my",
        "mongolia": "mp",
        "nepal": "np",
        "oman": "mk",
        "pakistan": "pk",
        "papuanewguinea": "pp",
        "paracelislands": "pf",
        "philippines": "ph",
        "qatar": "qa",
        "saudiarabia": "su",
        "singapore": "si",
        "spratlyisland": "xp",
        "srilanka": "ce",
        "syria": "sy",
        "tajikistan": "ta",
        "thailand": "th",
        "turkey": "tu",
        "turkmenistan": "tk",
        "unitedarabemirates": "ts",
        "uae": "ts",
        "uzbekistan": "uz",
        "vietnam": "vm",
        "westbankofthejordanriver": "wj",
        "westbank": "wj",
        "yemen": "ye",
        "bermudaislands": "bm",
        "bermuda": "bm",
        "bouvetisland": "bv",
        "caboverde": "cv",
        "faroeislands": "fa",
        "faroes": "fa",
        "falklandislands": "fk",
        "falklands": "fk",
        "sainthelena": "xj",
        "southgeorgiaandthesouthsandwichislands": "xs",
        "southgeorgia": "xs",
        "southsandwichislands": "xs",
        "belize": "bh",
        "costarica": "cr",
        "elsalvador": "es",
        "guatemala": "gt",
        "honduras": "ho",
        "nicaragua": "nq",
        "panama": "pn",
        "albania": "aa",
        "andorra": "an",
        "austria": "au",
        "belarus": "bw",
        "belgium": "be",
        "bosniaandherzegovina": "bn",
        "bosnia": "bn",
        "bosniaherzegovina": "bn",
        "herzegovina": "bn",
        "bulgaria": "bu",
        "croatia": "ci",
        "czechrepublic": "xr",
        "czechia": "xr",
        "denmark": "dk",
        "estonia": "er",
        "finland": "fi",
        "france": "fr",
        "germany": "gw",
        "gibraltar": "gi",
        "greece": "gr",
        "guernsey": "gg",
        "hungary": "hu",
        "iceland": "ic",
        "ireland": "ie",
        "isleofman": "im",
        "italy": "it",
        "jersey": "je",
        "kosovo": "kv",
        "latvia": "lv",
        "liechtenstein": "lh",
        "lithuania": "li",
        "luxembourg": "lu",
        "macedonia": "xn",
        "malta": "mm",
        "montenegro": "mo",
        "moldova": "mv",
        "monaco": "mc",
        "netherlands": "ne",
        "norway": "no",
        "poland": "pl",
        "portugal": "po",
        "serbia": "rb",
        "romania": "rm",
        "russia": "ru",
        "russianfederation": "ru",
        "sanmarino": "sm",
        "slovakia": "xo",
        "slovenia": "xv",
        "spain": "sp",
        "sweden": "sw",
        "switzerland": "sz",
        "ukraine": "un",
        "vaticancity": "vc",
        "serbiaandmontenegro": "yu",
        "serbia": "yu",
        "montenegro": "yu",
        "britishindianoceanterritory": "bi",
        "christmasisland": "xa",
        "cocosislands": "xb",
        "keelingislands": "xb",
        "comoros": "cq",
        "heardandmcdonaldislands": "hm",
        "maldives": "xc",
        "mauritius": "mf",
        "mayotte": "ot",
        "réunion": "re",
        "reunion": "re",
        "reunion": "re",
        "seychelles": "se",
        "americansamoa": "as",
        "cookislands": "cw",
        "fiji": "fj",
        "frenchpolynesia": "fp",
        "guam": "gu",
        "johnstonatoll": "ji",
        "kiribati": "gb",
        "marshallislands": "xe",
        "micronesia": "fm",
        "federatedstatesofmicronesia": "fm",
        "midwayislands": "xf",
        "nauru": "nu",
        "newcaledonia": "nl",
        "niue": "xh",
        "northernmarianaislands": "nw",
        "palau": "pw",
        "pitcairnisland": "pc",
        "samoa": "ws",
        "solomonislands": "bp",
        "tokelau": "tl",
        "tonga": "to",
        "tuvalu": "tv",
        "vanuatu": "nn",
        "wakeisland": "wk",
        "wallisandfutuna": "wf",
        "wallis": "wf",
        "futuna": "wf",
        "argentina": "ag",
        "bolivia": "bo",
        "brazil": "bl",
        "chile": "cl",
        "colombia": "ck",
        "ecuador": "ec",
        "frenchguiana": "fg",
        "guyana": "gy",
        "paraguay": "py",
        "peru": "pe",
        "surinam": "sr",
        "uruguay": "uy",
        "venezuela": "ve",
        "anguilla": "am",
        "antiguaandbarbuda": "aq",
        "antigua": "aq",
        "barbuda": "aq",
        "aruba": "aw",
        "bahamas": "bf",
        "barbados": "bb",
        "britishvirginislands": "vb",
        "caribbeannetherlands": "ca",
        "caymanislands": "cj",
        "cuba": "cu",
        "curaçao": "co",
        "curacao": "co",
        "dominica": "dq",
        "dominicanrepublic": "dr",
        "grenada": "gd",
        "guadeloupe": "gp",
        "haiti": "ht",
        "jamaica": "jm",
        "martinique": "mq",
        "montserrat": "mj",
        "puertorico": "pr",
        "saintbarthélemy": "sc",
        "saintbarthelemy": "sc",
        "saintkittsnevis": "xd",
        "saintkitts": "xd",
        "nevis": "xd",
        "saintlucia": "xk",
        "saintmartin": "st",
        "saintvincentandthegrenadines": "xm",
        "saintvincent": "xm",
        "thegrenadines": "xm",
        "grenadines": "xm",
        "sintmaarten": "sn",
        "trinidadandtobago": "tr",
        "trinidad": "tr",
        "tobago": "tr",
        "turksandcaicosislands": "tc",
        "virginislandsoftheunitedstates": "vi",
        "antarctica": "ay",
        "noplace": "xx",
        "unknown": "xx",
        "undetermined": "xx",
        "variousplaces": "vp",
        "various": "vp",
    }
    # normed_country = country.replace(" ", "").lower()
    normed_country = re.sub(r"[\s\-']", "", country).lower()
    try:
        result = countries[normed_country]
    except KeyError as e:
        if len({e}) < 4:
            logger.info(f"Advisory: assuming country name ({e}) has already been processed.")
        else:
            logger.warning(f"Warning: {e} is not a recognised country name; it has been passed on unchanged.")
        result = country
    return result


def norm_place(place):
    long_countries = {
        "england": "enk",
        "northernireland": "nik",
        "scotland": "stk",
        "wales": "wlk",

        "alberta": "abc",
        "britishcolumbia": "bcc",
        "bc": "bcc",
        "manitoba": "mbc",
        "newbrunswick": "nkc",
        "newfoundland": "nfc",
        "labrador": "nfc",
        "newfoundlandandlabrador": "nfc",
        "northwestterritories": "ntc",
        "novascotia": "nsc",
        "nunavut": "nuc",
        "ontario": "onc",
        "princeedwardisland": "pic",
        "québecprovince": "quc",
        "quebéc": "quc",
        "quebecprovince": "quc",
        "quebec": "quc",
        "saskatchewan": "snc",
        "yukonterritory": "ykc",
        "yukon": "ykc",

        "alabama": "alu",
        "alaska": "aku",
        "arizona": "azu",
        "arkansas": "aru",
        "california": "cau",
        "colorado": "cou",
        "connecticut": "ctu",
        "delaware": "deu",
        "districtofcolumbia": "dcu",
        "columbia": "dcu",
        "florida": "flu",
        "georgia": "gau",
        "hawaii": "hiu",
        "idaho": "idu",
        "illinois": "ilu",
        "indiana": "inu",
        "iowa": "iau",
        "kansas": "ksu",
        "kentucky": "kyu",
        "louisiana": "lau",
        "maine": "meu",
        "maryland": "mdu",
        "massachusetts": "mau",
        "michigan": "miu",
        "minnesota": "mnu",
        "mississippi": "msu",
        "missouri": "mou",
        "montana": "mtu",
        "nebraska": "nbu",
        "nevada": "nvu",
        "newhampshire": "nhu",
        "newjersey": "nju",
        "newmexico": "nmu",
        "newyork": "nyu",
        "newyorkstate": "nyu",
        "northcarolina": "ncu",
        "northdakota": "ndu",
        "ohio": "ohu",
        "oklahoma": "oku",
        "oregon": "oru",
        "pennsylvania": "pau",
        "rhodeisland": "riu",
        "southcarolina": "scu",
        "southdakota": "sdu",
        "tennessee": "tnu",
        "texas": "txu",
        "utah": "utu",
        "vermont": "vtu",
        "virginia": "vau",
        "washington": "wau",
        "washingtonstate": "wau",
        "westvirginia": "wvu",
        "wisconsin": "wiu",
        "wyoming": "wyu",

        "australiancapitalterritory": "aca",
        "queensland": "qea",
        "tasmania": "tma",
        "victoria": "vra",
        "westernaustralia": "wea",
        "newsouthwales": "xna",
        "northernterritory": "xoa",
        "southaustralia": "xra",
    }
    normed_place = place.replace(" ", "").lower()
    try:
        result = long_countries[normed_place]
    except KeyError as e:
        if len({e}) == 3:
            logger.info(f"Advisory: assuming place name ({e}) has already been processed.")
        else:
            logger.warning(f"Warning: {e} is not a recognised place name; it has been passed on unchanged.")
        result = place
    return result


def get_long_country(country, place):
    ## USA & UK return a detailed 3-digit code based on local region
    return place if len(place) == 3 else country


def norm_dates(raw):
    result = [date.strip() for date in raw.split(",")]
    return result


def norm_size(raw):
    raw = strip_unwanted(r"cm",raw)
    return int(raw)


def norm_pages(raw):
    raw = strip_unwanted(r"pages|\[|\]", raw)
    if "approximately" in raw:
        raw = re.sub(r"\s?approximately\s?", "", raw)
        raw = raw + "?"
    return raw


def norm_year(raw):
    raw = strip_unwanted(r"[\[\]]", raw)
    return raw


def strip_unwanted(pattern, raw):
  raw = re.sub(pattern, "", raw)
#   raw = norm_string(raw)
  return raw


def check_for_approx(raw):
    raw = str(raw).strip()
    if raw[-1] == "?":
        is_approx = True
        # raw = trim_mistaken_decimals(raw[:-1].rstrip())
        raw = raw[:-1].rstrip()
    else:
        is_approx = False
    raw = trim_mistaken_decimals(raw)
    return (raw, is_approx)


def trim_mistaken_decimals(string):
    if string.endswith(".0"):
        string = string[:-2]
    return string


def create_date_list(dates):
    dates = re.sub(r"\s", "", dates)
    dates = dates.replace(".0", "")
    dates = dates.split(",")
    return dates


def norm_excel_data(sheet):
    """
    excel seems pretty random in how it assigns string/int/float, so...
    this routine coerces everything into a string,
    strips ".0" from misrecognised floats
    & removes trailing spaces
    """
    tmp = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        tmp_row = []
        if not row[0]:
            break
        for col in row:
            if col:
                data = str(col).strip()
                data = trim_mistaken_decimals(data)
            else:
                data = ""
            tmp_row.append(data)
        tmp.append(tmp_row)
    return tmp


def parse_spreadsheet_data(sheet):
    current_time = datetime.now()
    records = []
    for row in norm_excel_data(sheet):
        cols = iter(row)
        sublibrary = next(cols)
        langs = norm_langs(next(cols))
        isbn = next(cols)
        title = Title(next(cols), next(cols))
        subtitle = Title(next(cols), next(cols))
        parallel_title = Title(next(cols), next(cols))
        parallel_subtitle = Title(next(cols), next(cols))
        country = norm_country(next(cols))
        place = next(cols)
        publisher = next(cols)
        pub_date, pub_date_is_approx = check_for_approx(norm_year(next(cols)))
        copyright_ = next(cols).replace("©","").strip()
        extent, extent_is_approx = check_for_approx(norm_pages(next(cols)))
        size = norm_size(next(cols))
        series_title = next(cols)
        series_enum = next(cols)
        note = next(cols)
        sale_code = next(cols)
        date_of_sale = create_date_list(next(cols))
        hol_notes = next(cols)
        donation = next(cols)
        barcode = next(cols)

        record = Record(
            sublibrary,
            langs,
            isbn,
            title,
            subtitle,
            parallel_title,
            parallel_subtitle,
            country,
            place,
            publisher,
            pub_date,
            copyright_,
            extent,
            size,
            series_title,
            series_enum,
            note,
            sale_code,
            date_of_sale,
            hol_notes,
            donation,
            barcode,

            pub_date_is_approx,
            extent_is_approx,
            current_time,

            sequence_number = 1,
            links = [880, []],
        )
        records.append(record)
        # pprint(record)
    return records


def build_000():
    """leader (0 is only for sorting purposes; should read 'LDR')"""
    content = "00000nam a22000003i 4500"
    return build_field(0, [[-2,-2, content]])


def build_005(record):
    """date & time of transaction
    "The date requires 8 numeric characters in the pattern yyyymmdd. The time requires 8 numeric characters in the pattern hhmmss.f, expressed in terms of the 24-hour (00-23) clock."
    """
    i1, i2 = -2, -2  ## "This field has no indicators or subfield codes."
    standard_time = record.timestamp.now(timezone.utc)
    ## NB: python produces this format: YYYY-MM-DD HH:MM:SS.ffffff, e.g. 2020-09-30 12:37:55.713351
    timestamp = str(standard_time).translate(str.maketrans("", "", " -:"))[:16]
    return build_field(5, [[i1, i2, timestamp]])


def build_008(record):
    """pub year & main language?"""
    i1, i2 = -2, -2  ## "Field has no indicators or subfield codes"
    t = record.timestamp
    date_entered_on_file = str(t.year)[2:] + str(t.month).zfill(2) + str(t.day).zfill(2)
    pub_status = "s"
    date_1 = record.pub_year
    date_2 = 4 * "|"
    place_of_pub = record.country.ljust(3, "\\")
    books_configuration = (14*"|") + "\\" + (2*"|")
    lang = record.langs[0].ljust(3, "\\")
    modified_and_cataloging = 2*"|"
    content = f"{date_entered_on_file}{pub_status}{date_1}{date_2}{place_of_pub}{books_configuration}{lang}{modified_and_cataloging}"
    return build_field(8, [[i1, i2, content]])


def build_033(record):
    """sales dates"""
    i1 = 0 if len(record.sale_dates) == 1 else 1
    i2 = -1
    content = f"$a{"$a".join(record.sale_dates)}"
    return build_field(33, [[i1, i2, content]])


def build_040():
    """catalogued in Oxford"""
    content = "$aUkOxU$beng$erda$cUkOxU"
    return build_field(40, [[-1,-1,content]])


def build_245(record):
    """Title
    Field 245 ends with a period, even when another mark of punctuation is present, unless the last word in the field is an abbreviation, initial/letter, or data that ends with final punctuation.
    """
    has_chinese_title = bool(record.title.transliteration)
    if has_chinese_title:
        title, subtitle = record.title.transliteration, record.subtitle.transliteration
        chinese_title = combine(record.title.original, record.subtitle.original)
        chinese_title = end_field_with_period(chinese_title)
        nonfiling = 0
        sequence_number = seq_num(record.sequence_number)
        linkage = f"$6880-{sequence_number}"
    else:
        title, subtitle = record.title.original, record.subtitle.original
        nonfiling, title = check_for_nonfiling(title)
        linkage = ""
    title = combine(title, subtitle) if title else ""
    title = end_field_with_period(title)
    i1, i2 = 0, nonfiling
    if has_chinese_title:
        build_880(record, chinese_title, i1, i2, "245", sequence_number)
    content = f"{linkage}$a{title}" if title else ""
    return build_field(245, [[i1, i2, content]])


def build_264(record):
    """publisher & copyright"""
    i1 = -1
    i2 = 1  ## "Publication: Field contains a statement relating to the publication, release, or issuing of a resource."
    # i2 = 0
    result = []
    place = f"$a{record.place} "
    publisher = f":$b{record.publisher}"
    pub_year = record.pub_year
    if record.pub_year_is_approx:
        pub_year = f"[{pub_year}?]"
    pub_year = f",$c{pub_year}"
    result.append([i1, i2, f"{place}{publisher}{pub_year}"])

    if record.copyright:
        ## WHY i2=4 ("Copyright notice date") subfield $c ("Date of production, publication, distribution, manufacture, or copyright notice (R)")??
        # result.append([i1, i2, f"$a\u00a9 {record.copyright}"])
        result.append([i1, -1, f"$a\u00a9 {record.copyright}"])
    return build_field(264, result)


def build_300(record):
    """physical description"""
    i1, i2 = -1, -1 ## "undefined"
    pages = f"{record.extent} pages"
    if record.extent_is_approx:
        pages = f"approximately {pages}"
    size = f"{record.size} cm"
    content = f"$a{pages} ;$c{size}"
    return build_field(300, [[i1, i2, content]])


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
    notes = record.hol_notes
    # notes = record.notes
    notes = f"$z{notes}" if notes else ""
    donation = f"$z{record.donation}" if record.donation else ""
    barcode = f"$p{record.barcode}" if record.barcode else ""
    content = f"{barcode}{donation}{notes}"
    return build_field(876, [[-1, -1, content]])


def build_904():
    """authority (boilerplate)"""
    return build_field(904, [[-1, -1, "$aOxford Local Record"]])


def build_024(record):  ##optional
    """sales code (if exists)"""
    i1 = 8
    i2 = -1
    content = f"$a{record.sales_code}" if record.sales_code else ""
    return build_field(24, [[i1, i2, content]])


def build_041(record):  ##optional
    """language codes if not monolingual"""
    # i1 = -1  ## "No information...as to whether the item is or includes a translation."
    i1 = 0  ## "No information...as to whether the item is or includes a translation."
    i2 = -1  ## "(followed by) MARC language code"
    content = ""
    is_multi_lingual = len(record.langs) > 1
    if is_multi_lingual:
        ## OPTION 1
        # if record.title.transliteration:
        #     main_lang = record.langs[0]
        #     others = record.langs[1:]
        #     lang_list = f"$a{"$a".join(others)}$h{main_lang}"
        # else:
        #     lang_list = f"$a{"$a".join(record.lang)}"
        ## OPTION 2
        # main_lang = record.langs[0]
        # others = record.langs[1:]
        # lang_list = f"$a{"$a".join(others)}$h{main_lang}"
        # result = (build_field(41, [[i1,i2, lang_list]]))
        ## OPTION 3
        content = f"$a{"$a".join(record.langs)}"
    return build_field(41, [[i1,i2, content]])


def build_246(record):  ##optional
    """
    Varying Form of Title
    Holds parallel Western title AND/OR original Chinese character title
    NB: Initial articles (e.g., The, La) are generally not recorded in field 246 unless the intent is to file on the article. [https://www.loc.gov/marc/bibliographic/bd246.html]
    """
    i1 = 3  ## "No note, added entry"
    i2 = 1  ## parallel title
    result = ""
    has_parallel_title = bool(record.parallel_title.original)
    has_chinese_parallel_title = bool(record.parallel_title.transliteration)
    linkage = "$6880-01" if has_chinese_parallel_title else ""
    if has_chinese_parallel_title:
        parallel_title = record.parallel_title.transliteration
        parallel_subtitle = record.parallel_subtitle.transliteration
        chinese_parallel_title = combine(record.parallel_title.original, record.parallel_subtitle.original)
        sequence_number = seq_num(record.sequence_number)
        linkage = f"$6880-{sequence_number}"
        build_880(record, chinese_parallel_title,i1, i2, "246", sequence_number)
    elif has_parallel_title:  ## (i.e. Western script)
        parallel_title, parallel_subtitle = record.parallel_title.original, record.parallel_subtitle.original
        # nonfiling, parallel_title = mark_nonfiling_words(parallel_title)
    else:
        parallel_title, parallel_subtitle = "", ""
    if parallel_title:
        parallel_title = "$a" + combine(parallel_title, parallel_subtitle)
    content = f"{linkage}{parallel_title}"
    return build_field(246, [[i1, i2, content]])


def build_490(record):  ## optional
    """Series Statement"""
    i1 = 0  ## Series not traced: No series added entry is desired for the series.
    i2 = -1
    series_title = f"$a{record.series_title}" if record.series_title else ""
    series_enum = f"$v{record.series_enum}" if record.series_enum else ""
    sep = " ;" if series_title and series_enum else ""
    content = series_title + sep + series_enum
    return build_field(490, [[i1, i2, content ]])


def build_500(record):  ##optional
    """general notes
    Punctuation - Field 500 ends with a period unless another mark of punctuation is present. If the final subfield is subfield $5, the mark of punctuation precedes that subfield.
    """
    # notes = record.hol_notes
    content = "$a" + end_field_with_period(record.notes) if record.notes else ""
    return build_field(500, [[-1, -1, content]])


def build_880(record, title, i1, i2, caller, sequence_number):  ##optional
    """Alternate Graphic Representation
    NB. unlike the other fields, this isn't called directly but by the linked field"""
    record.sequence_number += 1
    content = f"$6{caller}-{sequence_number}$a{title}"
    record.links[1].append(build_line(line_prefix("880"), i1, i2, content))


def build_field(numeric_tag, data):
    """
    silently suppresses optional fields if empty;
    stops with error if required field is empty
    """
    if not data:
        return ""
    is_optional_field = numeric_tag in optional_fields
    lines = []
    for line in data:
        i1 = expand_indicators(line[0])
        i2 = expand_indicators(line[1])
        content = line[2]
        if content:
            lines.append(build_line(line_prefix(numeric_tag), i1, i2, content))
        else:
            if not is_optional_field:
                logger.warning(f"Data for required field {str(numeric_tag).zfill(3)} is required.")
                raise MissingFieldError(f"Data for required field {str(numeric_tag).zfill(3)} is required.")
                # print(f"Warning: field {str(numeric_tag).zfill(3)} is empty")
            break
    result = (numeric_tag, lines) if lines else ""
    return result


def build_line(line_start, i1, i2, content):
    return (f"{line_start}{i1}{i2}{content}")


def line_prefix(numeric_tag):
    display_tag = "LDR" if numeric_tag == 0 else seq_num(numeric_tag)
    return f"={field_prefix(display_tag)}  "


def field_prefix(field_number):
    return str(field_number).zfill(3)


def seq_num(sequence_number):
    return str(sequence_number).zfill(2)


def expand_indicators(indicator):
    expansions = {-2: "", -1: "\\"}
    return expansions.get(indicator, indicator)


def combine(title, subtitle, sep=" :$b"):
    if subtitle:
        title += sep + subtitle
    return title


def end_field_with_period(text):
    text = text.strip()
    # print(f"******************* {text[-10:]}******************")
    if text and text[-1] not in "?!.":
        text = text + "."
    return text


def mark_nonfiling_words(title):
    nonfiling = 0
    if title:
        test = title.split("@@")
        if len(test) > 1:
            nonfiling = len(test[0])
            title = test[0] + test[1]
    return (nonfiling, title)


def check_for_nonfiling(title, lang="eng"):
    nonfiling_chars = {
        "eng": ("the", "a", "an"),
        "fr": ("le", "la", "les", "l'", "un", "une"),
        "it": ("lo", "il", "i", "l'", "gli", "le", "un", "una", "un'"),
        "sp": ("el", "la", "las", "los", "un", "una", "unos", "unas"),
        "gw": ("der", "die", "das", "ein", "eine"),
        "ne": ("de", "het"),
        "sw": ("en", "ett", "den", "det", "de"),
        "dk": ("en", "et"),
        "no": ("en", "ei", "et"),
        "po": ("o", "a", "os", "as", "um", "uma", "uns", "umas"),
        "chi": (),
    }
    # lang = "eng"
    break_char = "@@"
    nonfiling = title.find(break_char)
    result = (0, title)
    if nonfiling > 0:
        result = (nonfiling, title.replace(break_char, "", 1))
    else:
        for article in nonfiling_chars[lang]:
            test = re.match(f"({article}\\s?[^\\w\\s]?)\\w", title, re.I)
            if test:
                result = (test.span()[1] - 1, title)
                break
    return result


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
            build_490,
            build_876,
            build_024,
            build_041,
            build_246,
            build_500,
        ):
            field = step(record)
            if field:
                mark_record.append(field)
        if record.links:
            mark_record.append(record.links)
        mark_record.sort(key=lambda field: field[0])
        mark_records.append(mark_record)
    return mark_records


def write_mrk_file(data, file_name="output.mrk"):
    mrk_file_dir = Path("mrk_files")
    if not mrk_file_dir.is_dir():
        mrk_file_dir.mkdir()
        try:
            mrk_file_dir.mkdir()
            logger.info(f"Directory '{mrk_file_dir}' created successfully.")
        except FileExistsError:
            logger.info(f"Directory '{mrk_file_dir}' already exists.")
        except PermissionError:
            logger.warning(f"Permission denied: Unable to create '{mrk_file_dir}'.")
        except Exception as e:
            logger.warning(f"An error occurred: {e}")
    out_file = mrk_file_dir / file_name
    with open(out_file, "w", encoding="utf-8") as f:
        for record in data:
            for field in record:
                for line in field[1]:
                    # print(line)
                    f.write(line)
                    f.write("\n")
            f.write("\n")


def get_records(excel_file_address):
    excel_file = str(excel_file_address.resolve())
    workbook = load_workbook(filename=excel_file)
    sheet = workbook.active
    logger.info(f"\n{sheet.title} in {excel_file}")
    records = parse_spreadsheet_data(sheet)
    return records


def process_excel_file(excel_file_address):
    records = get_records(excel_file_address)
    mark_record_set = build_mark_records(records)
    write_mrk_file(mark_record_set, f"{excel_file_address.stem}.paul.mrk")
    # pprint(records)
    # for count, record in enumerate(records):
    #     print(f">> {count}")
    #     pprint(record)


def main():
    # process_excel_file(sys.argv[1])
    for file in Path("excel_files").glob("*.xlsx"):
        logger.info(f">>>>> processing: {file.name}")
        print(f">>>>> processing: {file.name}")
        process_excel_file(file)


if __name__ == "__main__":
    main()
