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
