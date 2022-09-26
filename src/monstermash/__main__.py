import json
import re
from functools import partial

import click
import questionary

from monstermash.crypt import Crypt

red = partial(click.style, fg='yellow')
blue = partial(click.style, fg='blue')
green = partial(click.style, fg='green')
danger = partial(click.style, fg='red')


def open_file(file):
    if re.search('.json$', file):
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        with open(file, 'r') as f:
            data = f.read()
    return data


@click.group()
def main():
    pass


@main.command()
def generate():
    keys = Crypt.generate()

    click.echo('-----------------')
    click.echo(red('Private Key (keep is secret, keep it safe)'))
    click.echo(red(keys.private_key.get_secret_value()))
    click.echo(blue('Public Key (you can share this one)'))
    click.echo(blue(keys.public_key.get_secret_value()))
    click.echo('-----------------')


@main.command()
def encrypt():
    private_key = questionary.password('Enter your private key:').ask()
    public_key = questionary.text('Enter the public key:').ask()
    crypt = Crypt(private_key.encode())

    input_type = questionary.select(
        'What type of data do you want to encrypt?', choices=['file', 'text']
    ).ask()

    if input_type == 'file':
        file = questionary.text('Enter the file path:').ask()
        data = open_file(file)
    else:
        data = questionary.password('Enter (or paste) the text to encrypt:').ask()

    encrypted = crypt.encrypt(data.encode(), public_key)
    click.echo(green(encrypted))


@main.command()
def decrypt():
    private_key = questionary.password('Enter your private key:').ask()
    public_key = questionary.text('Enter the public key:').ask()
    crypt = Crypt(private_key.encode())

    data = questionary.text('Enter the encrypted text:').ask()

    decrypted = crypt.decrypt(data.encode(), public_key)
    click.echo(green(decrypted.decode()))


if __name__ == '__main__':
    main()
