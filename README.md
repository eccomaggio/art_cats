# Overview of the project

This project consists of two basic parts:

1) a gui to display, enter, amend and delete records from a .csv (or .xslx excel file)
2) for defined .csv types, a CSV -> Marc 21 (rda) files

+ Each flavour of CSV has its own entry point (e.g. art.py for art auction catalogues). These are now deprecated.
+ Instead, there is a default mode (universal.py) for any flavour, which will automatically create a best-guess GUI or match the correct gui if it exists.

Any file that needs conversion to Marc21 requires the column structure (and GUI layout) to be defined in the specific entry file. Column names (programatically) must follow the conventions in the Record specified in mark_21.py - the actual text labels appearing in the GUI can be anything; they are set separately. The order of the columns can differ from the Marc21 Record (the mapping, if different) is set as a list of mappings for each item in **settings.csv_to_marc_mappings**.

Note that column names are always lower-case (important for field names and yaml file data)

There are many settings that can be tweaked.

I am currently migrating logic / io, etc. from the overstuffed form_gui.py into clearer homes (logic.py, io.py, etc.), but this is still on-going.

Validation is a little complicated:

There are two levels:

1. input record (strings)
2. MARC record (processed records)

## Validation can only be applied to known patterns

### To set up validation, fill in the following settings:

 .required_fields (i.e. columns)
 .mandatory_marc_fields
 .must_validate

### "dummy records"

These 'skip validation; and are a way of preserving anomalous records, e.g. because unfinished or for debugging. The 'validation_skip_text' is the text that should immediately start the 'validation_skip_fieldname'

### MARC file validation happens

1. parse_row()
2. individual builds [OR should i be more strict and validate before & assume perfect data?]

### Check for mandatory happens

1. apply_marc_logic() i.e. when building marc records
