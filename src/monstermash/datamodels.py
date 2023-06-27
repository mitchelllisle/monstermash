from pydantic import BaseModel, SecretStr


class KeyPair(BaseModel):
    private_key: SecretStr
    public_key: str
