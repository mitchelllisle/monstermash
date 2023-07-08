from monstermash.utils.file import open_file


def test_txt_file():
    content = open_file('tests/monstermash-lyrics.txt')
    assert content.startswith('I was working in the lab, late one night')


def test_json_file():
    content = open_file('tests/sample-data.json')
    assert content['artist'] == 'The Crypt-Kicker Five'
