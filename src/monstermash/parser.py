import os
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

        Raises:
            ValueError: If the file exists but is readable by group or others (POSIX only).
        """
        self._reject_loose_permissions()
        self.parser.read(self.config_file)
        return self.parser

    def write(self, config: ConfigParser):
        """
        Write a ConfigParser object to the configuration file with owner-only (0600) permissions.

        Private keys are stored in plaintext, so the file is created and kept at mode 0600 — the
        same trust model as an SSH private key.

        Args:
            config (ConfigParser): The ConfigParser object to be written to the file.
        """
        fd = os.open(self.config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            config.write(f)
        if os.name == 'posix':
            os.chmod(self.config_file, 0o600)

    def _reject_loose_permissions(self):
        """Refuse to read a config file that is accessible by group or others.

        Mirrors SSH's refusal to use over-permissive private key files. No-op on non-POSIX
        platforms and when the file does not yet exist.

        Raises:
            ValueError: If the file is group- or world-accessible.
        """
        if os.name != 'posix' or not os.path.exists(self.config_file):
            return
        if os.stat(self.config_file).st_mode & 0o077:
            raise ValueError(
                f'config file {self.config_file} is accessible by group/others; ' f'run: chmod 600 {self.config_file}'
            )
