# Overview of the project

This project consists of two basic parts:

1) a gui to display, enter, amend and delete records from a .csv (or .xslx excel file)
2) for defined .csv types, a CSV -> Marc 21 (rda) files

+ Each flavour of CSV has its own entry point (e.g. art.py for art auction catalogues).
+ In theory, there is a default mode (currently universal.py) for any flavour, which will automatically create a best-guess GUI; however, this has not been maintained and now needs repairing when I have time.

Any file that needs conversion to Marc21 requires the column structure (and GUI layout) to be defined in the specific entry file. Column names (programatically) must follow the conventions in the Record specified in mark_21.py - the actual text labels appearing in the GUI can be anything; they are set separately. The order of the columns can differ from the Marc21 Record (the mapping, if different) is set as a list of mappings for each item in **settings.csv_to_marc_mappings**.

There are many settings that can be tweaked.

I am currently migrating logic / io, etc. from the overstuffed form_gui.py into clearer homes (logic.py, io.py, etc.), but this is still on-going.
