# Overview of code

## Typehints

1. **atoms** = String | Subfield | Punctuation | Blank
2. **Subfield** = {code: str | int, data: str}; if code is -2, renders as a string
3. **Content** = list[atoms] | atoms
4. **Field** = {tag: int, i1, i2, contents: Content}
5. **fields** contain: subfields, or blanks or punctuation; bare strings are coded as subfields with no subcode
6. **marc_record** = list[Field]

To do:

This needs a rewrite to properly separate out data and GUI. Need to create a separate Data class to receive, manipulate, and deliver data from the .csv / .xslx 

- DONE - move Grid() from form_gui.py into logic.py
- sort out type errors with COL
- is there a simpler way to implement COL? i.e. a dataclass whose members can be iterated and map to another text field, e.g. COL.isbn -> .value = 1, .name = 'isbn', .title = "ISBN number"

- DONE - **check 'holding_notes'** - they seem to have different uses / marc fields between art_cats and strachan

- DONE - if file type recognized by universal.py, apply relevant settings
- DONE - remove redundant COL declarations from entry point files (when file-specific settings are plumbed in)
- DONE - rewrite art.py / strachan.py / orders.py to send headers/col_names to create COL on the fly
- DONE - add in a way to force a filetype on a file EVEN IF the headers don't match AS LONG AS the number of columns matches.

- DONE - make sure 'algorithmic display' still works for new csvs: create a "general" entry point which uses the algorithm to build gui
- DONE - allow record that is totally empty to be deleted (i.e. sum of all cols = "")
- DONE - save when leaving barcode field should only work when the record is unlocked
- DONE - illustrations should carry over when new record is created
- DONE - illustrations should default to 'none'?
- DONE - move logic out of form_gui.py into logic.py (so can easily switch GUIs)
- DONE - allow blank records to be saved & then delete them (allows user to delete a record by clearing it)
- DONE - stop submit record alert appearing twice
- DONE - robust indication of 1) changed field, 2) error in field
- DONE - make it so that barcode submits when the lineEdit loses focus, not when text changes (otherwise can't type it in manually!)
- DONE - moved common.py validation code into validation.py
- DONE (ongoing) - moved file functions from common.py into io.py
- DONE: not validating on lock
- DONE: i haven't migrated the specific validations to the new edit.py file for art catalogues
- DONE: migrate edit.py to new build scheme (in orderForm.py)
- DONE: add in fixes for Georgina's comments
- DONE: fix headers when you add first record
- add fixed min lengths to input boxes so they don't jump around when filled with long records
- DONE - add in validation (but how to deal with jumping between records?): ">> Choose" / isbn / notify / hold for /
- DONE: fix double "first select..." in follower inputs
- DONE: table view should read 'add a record...'
- DONE: make window title reflect name of the actual file being saved to
- DONE: "text changed": add to comboBoxes -> just add to .currentTextChanged.connect()
- DONE: "text changed": fix so doesn't appear when loading new record
- DONE: deal with 'custom_behaviour()' - probably not needed; ensure clear load on startup
- DONE: make an explicit lookup linking name of widget to option list in settings file (yaml)
- DONE: remove 'locked' sign from window title if locking disabled
- DONE: remove / deactivate 'lock' button if locking disabled
- DONE: highlight current record in table view
- DONE: highlight current record in table view IF has records on first load
- DONE: fixed combo box drop down selection
- DONE: made record lock toggle-able

### to make a combo box

load_record()
 ->> load_combo_box()
load_combo_box()
 ->> get_raw_combo_options()
 ->> get_normalized_combo_list()

*** load_combo_box() -> PERMUTATIONS:
A) leader:
 has record -> list matches name + set index to VALUE
 empty -> list matches to name
B) follower:
 has record -> list matches to leader's currentText + set index to VALUE
 empty -> list matches to leader's currentText

### To do in order form

1. DONE - implement fields to clear
1. implement QTableView to show records already entered (overview): click to amend
1. DONE - add in delete function (how about: type *del* or *delete* into ISBN field; on save, this will not be saved and will be deleted from the records)
1. DONE - add in search function: results appear as dropdown list = 3 inputs: text input -> 'go' button / 'end search' button -> dropdown list of rows returned
1. DONE - bring convert_pymarc.py up to date
1. DONE - harmonize edit.py & orderForm.py
1. DONE: add in layout hints: look for [filename].hint or failing that, any file ending .hint in the source file folder & use this (if heading count fits), else default to algorithmic layout
1. DONE - enable changes to data
1. DONE - enable saving changes to csv (or excel)
1. DONE - allow .csv / .tsv as source file
1. DONE - OK - enable adding a new record
1. DONE - make it command line based: edit,py -f data.csv/xls -h hintfile.hint -o output.csv
1. DONE - ?? add in field validation
1. DONE - add in smart extras, e.g. automatically add pub date from saledate; erase isbn etc. on 'New'
1. DONE - integrate more closely with art_cats.py
1. DONE - add in file explorer to open a new file
11 DONE - add the custom validation etc. to a 'custom_extensions' function
1. DONE - add a toggle-able help pane
1. DONE - (i think) - Ensure that the background of all input fields is white (not the case for QTextBox on windows
1. DONE - Ensure the window’s height is retained when the help pane is toggled
1. TOO DIFFICULT / ABANDONED - Make sure the column lines are respected (some look a bit wobbly…) – maybe an issue with horizontal alignment of the widget inside?
1. DONE - Add in validation e.g. warning if no barcode or pagination or title etc.
1. DONE - Save backup file on each submit (save to backup.bak)
1. DONE - ** consider logic of unlock button:
1. DONE - deal correctly with empty gui [title should read 'new']
think about this!
1. DONE Remove debug print out from barcode check
1. DONE Grey out ‘NEW’ button when entering a new record?? Or change to  ‘Abort record’ / ‘Abandon record’? and return to the previous record (save this as self.previous_record ?) OR add an ‘unlock’ button when a record comes up (i.e. existing records are default locked until you unlock them… NICE!)
1. DONE Make sure saved .csv doesn’t keep adding ‘.csv.csv’!!
MAYBE instead of changing background colour (coz difficult to do and makes display ugly), change colour of text in input boxes (grey) to show record is locked.

So:
make inputs locked (i.e. readonly + text = grey) by default
cannot be locked if text has been changed (-> abort button? or change button to 'lock': "this will wipe any changes you have made to this record. Do you want to proceed?" )
new records are unlocked

buttons:
**navigation** -> load record (+ reset styles), lock
**new record** -> reset styles, unlock
**submit record** -> validate, reset styles, lock
**clear** -> unlock
**load file** ->
**export as .csv**
**export as marc21**
**lock** -> validate
