from nacl.encoding import HexEncoder
from nacl.public import Box, PrivateKey, PublicKey

from monstermash.datamodels import KeyPair


class Crypt:
    """
    Crypt class provides methods for encryption and decryption of messages using NaCl (Salt) cryptographic library.

    Attributes:
        key_length (int): The length of the keys used in encryption/decryption. Default is 32.
    """

    key_length: int = 32

    def __init__(self, private_key: bytes, msg_encoder=HexEncoder, key_encoder=HexEncoder):
        """
        Initialize a new instance of Crypt class.

        Args:
            private_key (bytes): The private key used for encryption and decryption.
            msg_encoder (HexEncoder): Encoder used for encoding and decoding messages. Default is HexEncoder.
            key_encoder (HexEncoder): Encoder used for encoding and decoding keys. Default is HexEncoder.
        """
        self.msg_encoder = msg_encoder
        self.key_encoder = key_encoder
        self._private_key = PrivateKey(private_key, encoder=self.key_encoder)

    @property
    def private_key(self) -> bytes:
        """Get encoded private key.

        Returns:
            bytes: The encoded private key.
        """
        return self._private_key.encode(self.key_encoder)

    @property
    def public_key(self) -> bytes:
        """Get raw public key.

        Returns:
            bytes: The raw public key.
        """
        return self._private_key.public_key._public_key

    @property
    def encoded_public_key(self) -> bytes:
        """Get encoded public key.

        Returns:
            bytes: The encoded public key.
        """
        return self.key_encoder.encode(self.public_key)

    @classmethod
    def generate(cls, encoder=HexEncoder) -> KeyPair:
        """
        Generate a new private-public key pair.

        Args:
            encoder (HexEncoder): Encoder used for encoding the keys. Default is HexEncoder.

        Returns:
            KeyPair: A tuple containing the encoded private key and public key.
        """
        private_key = PrivateKey.generate()
        private_key_encoded = private_key.encode(encoder)
        public_key_encoded = private_key.public_key.encode(encoder)
        return KeyPair(private_key=private_key_encoded, public_key=public_key_encoded)

    def encrypt(self, msg: bytes, public_key: bytes) -> bytes:
        """
        Encrypt a message using a given public key. We append the public key to the ciphertext so that decryption
        becomes easy. The size of the key has to be consistent between encryption and decryption so that we can split
        the ciphertext based off the key size.

        Args:
            msg (bytes): The message to be encrypted.
            public_key (bytes): The public key used for encryption.

        Returns:
            bytes: The encrypted message.
        """
        secret = Box(self._private_key, PublicKey(public_key, encoder=self.key_encoder))
        encrypted = secret.encrypt(msg)
        formatted = b''.join([self.public_key, encrypted])
        return self.msg_encoder.encode(formatted)

    def decrypt(self, msg: bytes) -> bytes:
        """
        Decrypt a message using the private key.

        Args:
            msg (bytes): The message to be decrypted.

        Returns:
            bytes: The decrypted message.
        """
        decoded = self.msg_encoder.decode(msg)
        key = self.key_encoder.encode(decoded[: self.key_length])
        data = decoded[self.key_length :]
        secret = Box(self._private_key, PublicKey(key, encoder=self.key_encoder))
        return secret.decrypt(data)
