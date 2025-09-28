# Overview of code

## Typehints

1. **atoms** = String | Subfield | Punctuation | Blank
2. **Subfield** = {code: str | int, data: str}; if code is -2, renders as a string
3. **Content** = list[atoms] | atoms
4. **Field** = {tag: int, i1, i2, contents: Content}
5. **fields** contain: subfields, or blanks or punctuation; bare strings are coded as subfields with no subcode
6. **marc_record** = list[Field]

## To do:
1. add in layout hints: look for [filename].hint or failing that, any file ending .hint in the source file folder & use this (if heading count fits), else default to algorithmic layout
2. OK - enable changes to data
3. OK - enable saving changes to csv (or excel)
4. allow .csv / .tsv as source file
5. OK - enable adding a new record
5. make it command line based: edit,py -f data.csv/xls -h hintfile.hint -o output.csv
6. ?? add in field validation
7. ?? add in smart extras, e.g. automatically add pub date from saledate; erase isbn etc. on 'New'
8. integrate more closely with art_cats.py