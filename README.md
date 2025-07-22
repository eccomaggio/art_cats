Change logic of Result:
from Result(is_ok, is_error) Rust-style
to Result(is_ok: bool, data: Any), i.e. the flag tells you if the operation has succeeded, and the data carries either the successfully created data OR the error codes/messages