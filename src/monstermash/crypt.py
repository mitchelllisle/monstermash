from nacl.encoding import Base64Encoder, HexEncoder
from nacl.public import Box, PrivateKey, PublicKey
from pydantic import BaseModel, SecretStr


class KeyPair(BaseModel):
    private_key: SecretStr
    public_key: SecretStr


class Crypt:
    def __init__(self, private_key: bytes, msg_encoder=Base64Encoder, key_encoder=HexEncoder):
        self.msg_encoder = msg_encoder
        self.key_encoder = key_encoder
        self._private_key = PrivateKey(private_key, encoder=self.key_encoder)

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

    def encrypt(self, msg: bytes, public_key: bytes) -> str:
        secret = Box(self._private_key, PublicKey(public_key, encoder=self.key_encoder))
        encrypted = secret.encrypt(msg)
        return self.msg_encoder.encode(encrypted).decode()

    def decrypt(self, msg: bytes, public_key: bytes) -> bytes:
        decoded = self.msg_encoder.decode(msg)
        secret = Box(self._private_key, PublicKey(public_key, encoder=self.key_encoder))
        return secret.decrypt(decoded)
