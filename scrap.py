from dataclasses import dataclass, field
# from collections import defaultdict
from typing import List, Any, DefaultDict, Optional

@dataclass
class Sheet:
    """
    Represents a valid excel worksheet; as such, no further validation is made.
    """
    rows: List[List[Any]] = field(default_factory=list)

    def add_row(self, row_data: List[Any]):
        self.rows.append(row_data)

    def get_row(self, row_index: int) -> List[Any]:
        """ Retrieves a row by its index.  """
        if not (0 <= row_index < len(self.rows)):
            raise IndexError("Row index out of bounds.")
        return self.rows[row_index]

    def __len__(self) -> int:
        """ Returns the number of rows in the sheet.  """
        return len(self.rows)
