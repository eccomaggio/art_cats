# Overview of code

## Typehints

1. **atoms** = String | Subfield | Punctuation | Blank
2. **Subfield** = {code: str | int, data: str}; if code is -2, renders as a string
3. **Content** = list[atoms] | atoms
4. **Field** = {tag: int, i1, i2, contents: Content}
5. **fields** contain: subfields, or blanks or punctuation; bare strings are coded as subfields with no subcode
6. **marc_record** = list[Field]

orderForm:

to make a combo box:

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


To do in order form:
1. DONE - implement fields to clear
2. implement QTableView to show records already entered (overview): click to amend



List of things that work:
1. correctly loads records from file
2. correctly updates records
3. correctly saves records


List of things that don't:



## To do:

1. add in delete function (how about: type *del* or *delete* into ISBN field; on save, this will not be saved and will be deleted from the records)
2. add in search function: results appear as dropdown list = 3 inputs: text input -> 'go' button / 'end search' button -> dropdown list of rows returned
3. bring convert_pymarc.py up to date
4. harmonize edit.py & orderForm.py

1. DONE: add in layout hints: look for [filename].hint or failing that, any file ending .hint in the source file folder & use this (if heading count fits), else default to algorithmic layout
2. DONE - enable changes to data
3. DONE - enable saving changes to csv (or excel)
4. DONE - allow .csv / .tsv as source file
5. DONE - OK - enable adding a new record
6. DONE - make it command line based: edit,py -f data.csv/xls -h hintfile.hint -o output.csv
7. DONE - ?? add in field validation
8. DONE - add in smart extras, e.g. automatically add pub date from saledate; erase isbn etc. on 'New'
9. DONE - integrate more closely with art_cats.py
10. DONE - add in file explorer to open a new file
11. DONE - add the custom validation etc. to a 'custom_extensions' function
12. DONE - add a toggle-able help pane


1. DONE - (i think) - Ensure that the background of all input fields is white (not the case for QTextBox on windows
2. DONE - Ensure the window’s height is retained when the help pane is toggled
3. TOO DIFFICULT / ABANDONED - Make sure the column lines are respected (some look a bit wobbly…) – maybe an issue with horizontal alignment of the widget inside?
4. DONE - Add in validation e.g. warning if no barcode or pagination or title etc.
5. DONE - Save backup file on each submit (save to backup.bak)
6. DONE - ** consider logic of unlock button:
7. DONE - deal correctly with empty gui [title should read 'new']
think about this!

8. DONE Remove debug print out from barcode check

9. DONE Grey out ‘NEW’ button when entering a new record?? Or change to  ‘Abort record’ / ‘Abandon record’? and return to the previous record (save this as self.previous_record ?) OR add an ‘unlock’ button when a record comes up (i.e. existing records are default locked until you unlock them… NICE!)

10. DONE Make sure saved .csv doesn’t keep adding ‘.csv.csv’!!
MAYBE instead of changing background colour (coz difficult to do and makes display ugly), change colour of text in input boxes (grey) to show record is locked.


so:
make inputs locked (i.e. readonly + text = grey) by default
cannot be locked if text has been changed (-> abort button? or change button to 'lock': "this will wipe any changes you have made to this record. Do you want to proceed?" )
new records are unlocked

UNLOCKING:
1. simply unlock (no complications)

LOCKING:
1. save record and lock - if not yet finished, finish or abort [how to abort?]

currently, unlocking behaviour OK but doesn't grey out when first load record.
Also, make protocols, i.e. what can happen, e.g.:
- open empty & load file
- open from command line (really???)
- lock / unlock with record
- create new record: lock / unlock... etc.
test for these!



if filename given at commandline:
  open file [as currently]

if no file given OR file not found:


- load a default, empty record set
- create a save file option

Create a .hint file:

- name of headers + no. of columns
- default layout

********* CURRENT CRISIS:
fucked up the loading of records :S

buttons:
__navigation__ -> load record (+ reset styles), lock
__new record__ -> reset styles, unlock
__submit record__ -> validate, reset styles, lock
__clear__ -> unlock
__load file__ ->
__export as .csv__
__export as marc21__
__lock__ -> validate



