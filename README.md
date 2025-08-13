


atoms = String | Subfield | Punctuation | Blank
Subfield = {code: str | int, data: str}; if code is -2, renders as a string
Content = list[atoms] | atoms
Field = {tag: int, i1, i2, contents: Content}

marc_record = list[Field]

(String is str but with to_string() & to_mrc() methods, serialisable)



fields contain: subfields, or blanks or punctuation or bare strings