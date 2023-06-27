from nacl.encoding import HexEncoder
from nacl.public import Box, PrivateKey, PublicKey

from monstermash.datamodels import KeyPair


class Crypt:
    key_length: int = 32

    def __init__(self, private_key: bytes, msg_encoder=HexEncoder, key_encoder=HexEncoder):
        self.msg_encoder = msg_encoder
        self.key_encoder = key_encoder
        self._private_key = PrivateKey(private_key, encoder=self.key_encoder)

    @property
    def private_key(self) -> bytes:
        return self._private_key.encode(self.key_encoder)

    @property
    def public_key(self) -> bytes:
        return self._private_key.public_key._public_key

    @property
    def encoded_public_key(self) -> bytes:
        return self.key_encoder.encode(self.public_key)

    @classmethod
    def generate(cls, encoder=HexEncoder) -> KeyPair:
        private_key = PrivateKey.generate()
        private_key_encoded = private_key.encode(encoder)
        public_key_encoded = private_key.public_key.encode(encoder)
        return KeyPair(private_key=private_key_encoded, public_key=public_key_encoded)

    def encrypt(self, msg: bytes, public_key: bytes) -> bytes:
        secret = Box(self._private_key, PublicKey(public_key, encoder=self.key_encoder))
        encrypted = secret.encrypt(msg)
        formatted = b''.join([self.public_key, encrypted])
        return self.msg_encoder.encode(formatted)

    def decrypt(self, msg: bytes) -> bytes:
        decoded = self.msg_encoder.decode(msg)
        key = self.key_encoder.encode(decoded[: self.key_length])
        data = decoded[self.key_length :]
        secret = Box(self._private_key, PublicKey(key, encoder=self.key_encoder))
        return secret.decrypt(data)
