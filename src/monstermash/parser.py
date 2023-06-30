from configparser import ConfigParser


class ConfigManager:
    """ConfigManager

    ConfigManager class manages the reading and writing operations to a configuration file. This is useful for
    generating a set of keys (using `monstermash generate`) that will be used for future encryption and decryption
    operations
    """

    def __init__(self, config_file: str):
        """
        Initialize a new instance of ConfigManager class.

        Args:
            config_file (str): The path of the configuration file. Will default to ~/.monstermashcfg
        """
        self.parser = ConfigParser()
        self.config_file = config_file

    def read(self) -> ConfigParser:
        """
        Read the configuration file and returns a ConfigParser object.

        Returns:
            ConfigParser: The ConfigParser object with the contents of the configuration file.
        """
        self.parser.read(self.config_file)
        return self.parser

    def write(self, config: ConfigParser):
        """
        Write a ConfigParser object to the configuration file.

        Args:
            config (ConfigParser): The ConfigParser object to be written to the file.
        """
        with open(self.config_file, 'w+') as f:
            config.write(f)
