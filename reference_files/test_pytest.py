# import unittest
import pytest
from excel_to_marc21 import run
import re

def is_palindrome(string):
    string = re.sub(r'[.?! ]', '', string.lower())
    return string == string[::-1]

@pytest.mark.parametrize("palindrome", [
    "",
    "a",
    "Bob",
    "Never odd or even",
    "Do geese see God?",
])

def test_is_palindrome(palindrome):
    assert is_palindrome(palindrome)

@pytest.mark.parametrize("non_palindrome", [
    "abc",
    "abab",
])
def test_is_palindrome_not_palindrome(non_palindrome):
    assert not is_palindrome(non_palindrome)

if __name__ == "__main__":
  pass