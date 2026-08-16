"""
PATTERN OVERVIEW:

The diagnostic_columns:
1) to identify the pattern, the first 3 letters of the title of this column should match that in the csv
2) these diagnostic columns should be chosen to be both diagnostic and unlikely to change (e.g. 'barcode' is safe, although it is nearly always the last column;
'publication date' isn't great coz it could be 'date of publication'...)

The columns sequence == the order in the dictionary

The 'row_span' etc. refers to the position & size of the widget in the GUI
"""
known_patterns = {
  "art_cats": {
    "diagnostic_columns": [13, 27],
    "gui_column_count": 6,
    ## row_span, col_span, start_row, start_col, widget-type, name, title,
    "column_info": [
      [1, 2, 0, 0, "combo", "sublib", "Library"],
      [1, 2, 0, 2, "line", "langs", "language of resource"],
      [1, 2, 0, 4, "line", "isbn", "ISBN"],
      [2, 3, 1, 0, "text", "title", "Title"],
      [2, 3, 1, 3, "text", "tr_title", "Title transliteration"],
      [2, 3, 3, 0, "text", "subtitle", "Subtitle"],
      [2, 3, 3, 3, "text", "tr_subtitle", "Subtitle transliteration"],
      [2, 3, 5, 0, "text", "parallel_title", "Parallel title (dual language only)"],
      [2, 3, 5, 3, "text", "tr_parallel_title", "Parallel title transliteration"],
      [2, 3, 7, 0, "text", "parallel_subtitle", "Parallel subtitle (dual language only)"],
      [2, 3, 7, 3, "text", "tr_parallel_subtitle", "Parallel subtitle transliteration"],
      [1, 2, 13, 0, "line", "country_name", "Country of publication"],
      [1, 4, 13, 2, "line", "place", "(State,) City of publication"],
      [1, 3, 14, 0, "line", "publisher", "Publisher's name"],
      [1, 1, 14, 3, "line", "pub_year", "Year of publication"],
      [1, 1, 14, 4, "line", "copyright", "Year of copyright"],
      [1, 1, 15, 1, "line", "pagination", "Pages"],
      [1, 1, 15, 0, "line", "size", "Size"],
      [1, 1, 14, 5, "combo", "illustrations", "Illustrations"],
      [1, 3, 12, 0, "line", "series_title", "Series title"],
      [1, 2, 12, 3, "line", "series_enum", "Series enumeration"],
      [1, 1, 12, 5, "line", "volume", "Volume"],
      [3, 3, 9, 0, "text", "notes", "Note"],
      [1, 2, 15, 2, "line", "sales_code", "Sale code"],
      [1, 2, 15, 4, "line", "sale_dates", "Date of auction"],
      [3, 3, 9, 3, "text", "hol_notes", "HOL notes"],
      [1, 4, 16, 0, "line", "donation", "Donor note"],
        [1, 2, 16, 4, "line", "barcode", "Barcode"],
    ],
  },



  "strachan": {
    "diagnostic_columns": [4, 13],
    "gui_column_count": 6,
    "column_info": [
      (1, 2, 0, 0, "line", "langs", "Language of resource"),
      (1, 2, 0, 2, "line", "isbn","ISBN"),
      (2, 3, 1, 0, "text", "title","Title"),
      (2, 3, 1, 3, "text", "subtitle", "Subtitle"),
      (1, 2, 0, 4, "line", "artist", "Artist"),
      (1, 3, 3, 0, "line", "place", "(State,) City of publication"),
      (1, 3, 3, 3, "line", "country_name", "Country of publication"),
      (1, 2, 4, 0, "line", "publisher", "Publisher's name"),
      (1, 1, 4, 2, "line", "pub_year", "Year of publication"),
      (1, 1, 4, 3, "line", "copyright", "Year of copyright"),
      (1, 1, 4, 4, "line", "pagination", "Simple pagination"),
      (1, 1, 4, 5, "line", "size", "Height of item"),
      (2, 2, 6, 0, "text", "notes", "Note"),
      (1, 4, 5, 0, "line", "authors", "Author(s)"),
      (1, 2, 5, 4, "line", "call_number", "Call number"),
      (2, 2, 6, 2, "text", "hol_notes", "Holding note"),
      (1, 2, 7, 4, "line", "barcode", "Barcode"),
    ],
  },


  "orders": {
    "diagnostic_columns": [0, 1],
    "gui_column_count": 6,
    "column_info": [
      (1, 2, 0, 0, "combo", "subject_consultant", "Subject consultant"),
      (1, 2, 1, 0, "combo", "fund_code", "Fund code"),
      (1, 2, 2, 0, "combo", "order_type", "Order type"),
      (2, 6, 3, 0, "text", "bib_info", "Bibliographic information"),
      (1, 2, 7, 0, "line", "creator", "Creator"),
      (1, 2, 7, 2, "line", "date", "Publishing date"),
      (1, 2, 7, 4, "line", "isbn", "ISBN"),
      (1, 2, 0, 2, "combo", "library", "Library"),
      (1, 2, 1, 2, "combo", "location", "Location"),
      (1, 2, 2, 2, "combo", "item_policy", "Item policy"),
      (1, 2, 0, 4, "combo", "reporting_code_1", "Reporting code 1"),
      (1, 2, 1, 4, "combo", "reporting_code_2", "Reporting code 2"),
      (1, 2, 2, 4, "combo", "reporting_code_3", "Reporting code 3"),
      (1, 2, 8, 0, "line", "hold_for", "Hold for"),
      (1, 2, 9, 0, "line", "notify", "Notify"),
      (2, 4, 8, 2, "text", "additional_info", "Additional order instructions"),
    ],
  },


}
