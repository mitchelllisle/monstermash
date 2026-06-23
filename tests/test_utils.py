from monstermash.utils.file import open_file, read_text


def test_txt_file():
    content = open_file('tests/monstermash-lyrics.txt')
    assert content.startswith('I was working in the lab, late one night')


def test_json_file():
    content = open_file('tests/sample-data.json')
    assert content['artist'] == 'The Crypt-Kicker Five'


def test_read_text_returns_string():
    content = read_text('tests/monstermash-lyrics.txt')
    assert content.startswith('I was working in the lab, late one night')


def test_read_text_does_not_parse_json():
    # read_text always returns raw text, even for .json — so encrypt --file never gets a dict
    content = read_text('tests/sample-data.json')
    assert isinstance(content, str)
    assert content.strip().startswith('{')
