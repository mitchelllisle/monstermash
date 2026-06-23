import json
import re
from typing import Union

from pydantic import Json

NEW_LINE_EXPR = re.compile(r'[\n\r]')


def open_file(file) -> Union[Json, str]:
    """
    Open a file and return its contents. For JSON files, the contents are returned as a dictionary.
    For non-JSON files, the contents are returned as a string.

    Args:
        file (str): The path to the file to open.

    Returns:
        Union[dict, str]: The contents of the file. If the file is a JSON file, a dictionary is returned. Otherwise, a
            string is returned.
    """
    if re.search('.json$', file):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        with open(file, 'r') as f:
            data = f.read()
    return data


def read_text(file) -> str:
    """Read a file's raw contents as text.

    Unlike :func:`open_file`, this never parses JSON — it always returns the file's text verbatim,
    which is what the encrypt/decrypt commands operate on.

    Args:
        file (str): The path to the file to read.

    Returns:
        str: The file contents as text.
    """
    with open(file, 'r') as f:
        return f.read()
