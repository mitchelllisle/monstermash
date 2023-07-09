from configparser import ConfigParser
from typing import Optional

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from nacl import secret
from nacl.encoding import HexEncoder
from pydantic import SecretBytes


class ConfigManager:
    """ConfigManager

    ConfigManager class manages the reading and writing operations to a configuration file. This is useful for
    generating a set of keys (using `monstermash generate`) that will be used for future encryption and decryption
    operations
    """

    salt = SecretBytes(b'381ead4e310ca929ae7527c3cd850fac')

    def __init__(self, config_file: str):
        """
        Initialize a new instance of ConfigManager class.

        Args:
            config_file (str): The path of the configuration file. Will default to ~/.monstermashcfg
        """
        self.parser = ConfigParser()
        self.config_file = config_file
        self.kdf = Scrypt(
            salt=self.salt.get_secret_value(),
            length=32,
            n=2**14,
            r=8,
            p=1,
        )

    def read(self) -> ConfigParser:
        """
        Read the configuration file and returns a ConfigParser object.

        Returns:
            ConfigParser: The ConfigParser object with the contents of the configuration file.
        """
        self.parser.read(self.config_file)
        return self.parser

    def _encrypt_private_key_with_key(self, private_key: str, password: str) -> str:
        key = self.kdf.derive(password.encode()).hex()
        safe = secret.SecretBox(key.encode(), encoder=HexEncoder)
        return safe.encrypt(private_key.encode()).hex()

    def decrypt_private_key_with_key(self, ciphertext: str, password: str) -> str:
        key = self.kdf.derive(password.encode()).hex()
        safe = secret.SecretBox(key.encode(), encoder=HexEncoder)
        return safe.decrypt(ciphertext.encode()).decode()

    def write(
        self, config: ConfigParser, profile: str, private_key: str, public_key: str, password: Optional[str] = None
    ):
        """
        Write a ConfigParser object to the configuration file.

        Args:
            config (ConfigParser): The ConfigParser object to be written to the file.
            password (Optional[bytes])
            public_key:
            private_key:
            profile:
        """
        with open(self.config_file, 'w+') as f:
            payload = {'private_key': private_key, 'public_key': public_key, 'protected': 'no'}
            if password:
                payload['protected'] = 'yes'
                payload['private_key'] = self._encrypt_private_key_with_key(private_key, password)
            config[profile] = payload
            config.write(f)
