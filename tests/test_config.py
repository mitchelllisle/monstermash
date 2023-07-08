from monstermash.config import Config


def test_config_defaults():
    config = Config()
    assert config.config_file.endswith('.monstermashcfg')


def test_config():
    test_location = 'test_location'
    config = Config(config_file=test_location)
    assert config.config_file == test_location
