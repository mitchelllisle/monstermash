from typing import Optional

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

    A profile is either an owned keypair (both keys) or a *contact* — a recipient's
    public key with no private key, usable only as an encryption target.

    Attributes:
        private_key (Optional[SecretStr]): The profile's private key; ``None`` for a contact.
        public_key (str): The profile's public key.
    """

    private_key: Optional[SecretStr] = None
    public_key: str
