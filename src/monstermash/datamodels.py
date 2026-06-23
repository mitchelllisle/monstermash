from pydantic import BaseModel, SecretStr


class KeyPair(BaseModel):
    """
    KeyPair class representing a pair of private and public keys.

    Attributes:
        private_key (SecretStr): The private key used in the encryption or decryption process.
        public_key (str): The public key used in the encryption or decryption process.
    """

    private_key: SecretStr
    public_key: str


class ProfileConfig(BaseModel):
    """Keys stored under a single profile in the Monstermash config file.

    Attributes:
        private_key (SecretStr): The profile's private key.
        public_key (str): The profile's public key.
    """

    private_key: SecretStr
    public_key: str
