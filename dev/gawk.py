import sys
import os
import re

"""
this script reads in a csv and surrounds the fields in columns 1, 2 & the last one in double quotes.

it replicates the following (g)AWK script:

gawk '
BEGIN {
    FPAT = "([^,]*)|(\"[^\"]*\")"
    OFS = ","
}
{
    # Check fields 1, 2, and 7 (0-indexed: $1, $2, $7)
    # Add surrounding double quotes if not already present
    if ($1 !~ /^".*"$/) $1 = "\"" $1 "\""
    if ($2 !~ /^".*"$/) $2 = "\"" $2 "\""
    if ($7 !~ /^".*"$/) $7 = "\"" $7 "\""

    # Print record enclosed in parentheses and terminated by a comma
    print "(" $0 "),"
}' input.csv
"""


def process_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    base, ext = os.path.splitext(file_path)
    suffix = ext.lstrip(".")
    output_path = f"{base}.gawk.{suffix}"
    field_separator = ","

    try:
        with (
            open(file_path, "r", newline="", encoding="utf-8") as infile,
            open(output_path, "w", newline="", encoding="utf-8") as outfile,
        ):

            for line in infile:
                line_as_record = process_line(line, field_separator)
                line_as_record = f"[{line_as_record}]"
                outfile.write(f"{line_as_record},\n")

        print(f"Success! Processed file saved as: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def field_split_by_pattern(line: str, field_separator=",") -> list:
    # Replicate GAWK FPAT field splitting
    if not line:
        return [""]
    fields = []
    pos = 0
    while pos < len(line):
        # Match EITHER a string inside quotes, OR any sequence of non-comma characters
        # for lines like: Robotics,"London, UK",2026 (3 fields, not 4)
        match = re.match(r'"[^"]*"|[^,]*', line[pos:])
        if match:
            fields.append(match.group(0))
            pos += match.end()
        # if pos < len(line) and line[pos] == ",":
        if pos < len(line) and line[pos] == field_separator:
            pos += 1
            if pos == len(line):
                fields.append("")
    return fields


def normalise_column_count(fields:list, col_count:int) -> list:
    # Fill missing columns up to field 7 if line is shorter
    while len(fields) < col_count:
        fields.append("")
    return fields


def wrap_field_in_quotes(field: str, open_quote="\"", close_quote="\"") -> str:
  if not close_quote:
    close_quote = open_quote
  if not (field.startswith(open_quote) and field.endswith(close_quote)):
      return f"{open_quote}{field}{close_quote}"
  else:
      return field


def write_dictionary_entry(key: str, value: str | int) -> str:
    return f'{wrap_field_in_quotes(key)}: {value}'


def reorder_fields_to(fields:list, new_sequence:list[int]) -> list:
    if len(fields) != len(new_sequence):
        raise ValueError("Length of fields and new_sequence must match.")
    return [fields[i] for i in new_sequence]


def process_line(raw_line, field_separator) -> str:
    """
    Place all processing instructions in here.
    Remember, this is line-by-line only
    """

    line = raw_line.rstrip("\r\n")
    fields = field_split_by_pattern(line, field_separator)
    fields = normalise_column_count(fields, 7)

    target_indices = [0, 1, 6]  # Make fields 1,2,7 into strings
    # col_names = ["name", "title", "row_span", "col_span", "start-row", "start-col", "widget"]
    col_names = []

    for i, value in enumerate(fields):
        if i in target_indices:
          fields[i] = wrap_field_in_quotes(value)

        if col_names:
            fields[i] = write_dictionary_entry(col_names[i], fields[i])

    fields = reorder_fields_to(fields, [2, 3, 4, 5, 6, 0, 1])

    return ",".join(fields)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    process_csv(sys.argv[1])
