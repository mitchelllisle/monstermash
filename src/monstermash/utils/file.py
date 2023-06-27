import json
import re

NEW_LINE_EXPR = re.compile(r'[\n\r]')


def open_file(file):
    if re.search('.json$', file):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        with open(file, 'r') as f:
            data = f.read()
    return data
