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
