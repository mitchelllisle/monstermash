from configparser import ConfigParser


class ConfigManager:
    def __init__(self, config_file: str):
        self.parser = ConfigParser()
        self.config_file = config_file

    def read(self) -> ConfigParser:
        self.parser.read(self.config_file)
        return self.parser

    def write(self, config: ConfigParser):
        with open(self.config_file, 'w+') as f:
            config.write(f)
