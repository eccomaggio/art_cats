# Overview of code

## Typehints

1. **atoms** = String | Subfield | Punctuation | Blank
2. **Subfield** = {code: str | int, data: str}; if code is -2, renders as a string
3. **Content** = list[atoms] | atoms
4. **Field** = {tag: int, i1, i2, contents: Content}
5. **fields** contain: subfields, or blanks or punctuation; bare strings are coded as subfields with no subcode
6. **marc_record** = list[Field]

## To do:

1. DONE: add in layout hints: look for [filename].hint or failing that, any file ending .hint in the source file folder & use this (if heading count fits), else default to algorithmic layout
2. DONE - enable changes to data
3. DONE - enable saving changes to csv (or excel)
4. DONE - allow .csv / .tsv as source file
5. DONE - OK - enable adding a new record
6. DONE - make it command line based: edit,py -f data.csv/xls -h hintfile.hint -o output.csv
7. ?? add in field validation
8. DONE - add in smart extras, e.g. automatically add pub date from saledate; erase isbn etc. on 'New'
9. DONE - integrate more closely with art_cats.py
10. DONE - add in file explorer to open a new file
11. DONE - add the custom validation etc. to a 'custom_extensions' function

if filename given at commandline:
  open file [as currently]

if no file given OR file not found:

- load a default, empty record set
- create a save file option

Create a .hint file:

- name of headers + no. of columns
- default layout




