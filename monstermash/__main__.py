from monstermash.crypt import Crypt
import click
import json
import re
from pydantic import BaseModel
from typing import Optional


class Args(BaseModel):
    action: str
    private_key: Optional[str]
    public_key: Optional[str]
    file: Optional[str]


def open_file(file):
    if re.search(".json$", file):
        with open(file, "r") as f:
            data = json.load(f)
    else:
        with open(file, "r") as f:
            data = f.read()
    return data


def generate(args: Args) -> str:
    keys = Crypt.generate()
    return f"PrivateKey: {keys.private_key}\nPublicKey: {keys.public_key}"


def encrypt(args: Args) -> str:
    crypt = Crypt(args.private_key)
    data = open_file(args.file)
    encrypted = crypt.encrypt(data.encode(encoding="utf-8"), args.public_key)
    return encrypted


def decrypt(args: Args) -> str:
    crypt = Crypt(args.private_key)
    data = open_file(args.file)
    encrypted = crypt.decrypt(data, args.public_key)
    return encrypted.decode()


actions = {
    "generate": generate,
    "encrypt": encrypt,
    "decrypt": decrypt
}


@click.command()
@click.option('--action', default="encrypt", help='Whether to Encrypt or Decrypt')
@click.option('--private-key', help='Your private key for encrypted and decryption')
@click.option('--public-key', help='The Public Key you want to encrypt with')
@click.option('--file', help='The file you want to encrypt')
def main(**kwargs):
    args = Args(**kwargs)
    func = actions[args.action]
    output = func(args)
    print(output)


if __name__ == "__main__":
    main()
