from typing import Mapping, Optional

import click

from monstermash.config import Config
from monstermash.crypt import Crypt
from monstermash.parser import ConfigManager
from monstermash.utils.file import NEW_LINE_EXPR, open_file


@click.group()
@click.pass_context
def mash(ctx):
    config = Config()
    ctx.obj = ConfigManager(config.config_file)


@mash.command()
def generate():
    keys = Crypt.generate()

    click.echo('-----------------')
    click.echo('Private Key (keep it secret, keep it safe)')
    click.echo(keys.private_key.get_secret_value())
    click.echo('Public Key (you can share this one)')
    click.echo(keys.public_key)
    click.echo('-----------------')


@mash.command()
@click.pass_obj
@click.option(
    '--profile',
    prompt='Profile name',
    default='default',
    help='The name of the profile you want to create.',
)
@click.option('--private-key', prompt='Your private key', help='Your private key.')
@click.option('--public-key', prompt='Your public key', help='Your public key.')
def configure(config_manager: ConfigManager, profile: str, private_key: str, public_key: str):
    config = config_manager.read()
    config[profile] = {'private_key': private_key, 'public_key': public_key}
    config_manager.write(config)
    click.echo('.monstermashcfg file in your root directory contains the config')


@mash.command()
@click.pass_obj
@click.option('--profile', default=None)
@click.option('--private-key', default=None, help='Your private key.')
@click.option('--public-key', default=None, help='Your public key.')
@click.option('--file', default=None, help='The path to the file you want to encrypt')
@click.option('--data', default=None, help='Input data you want to encrypt')
def encrypt(
    config_manager: ConfigManager,
    profile: Optional[str],
    private_key: Optional[str],
    public_key: Optional[str],
    file: Optional[str],
    data: Optional[str],
):
    if profile is not None:
        config = config_manager.read()
        private_key = config[profile]['private_key']
        public_key = config[profile]['public_key'] if public_key is None else public_key

    if private_key is None:
        raise ValueError('you must specify either a private key or profile')

    crypt = Crypt(private_key.encode())

    if file is not None:
        data = open_file(file)

    if data is None:
        raise ValueError('you must specify either --file or --data')

    if public_key is None:
        raise ValueError('a public key is required for encryption')

    encrypted = crypt.encrypt(data.encode(), public_key.encode())
    click.echo(encrypted)


@mash.command()
@click.pass_obj
@click.option('--profile', default=None)
@click.option('--private-key', default=None, help='Your private key.')
@click.option('--file', default=None, help='The path to the file you want to encrypt')
@click.option('--data', default=None, help='Input data you want to encrypt')
def decrypt(
    config_manager: ConfigManager,
    profile: Optional[str],
    private_key: Optional[str],
    file: Optional[str],
    data: Optional[str],
):
    if profile is not None:
        config = config_manager.read()
        private_key = config[profile]['private_key']

    if private_key is None:
        raise ValueError('you must specify either a private key or profile')

    crypt = Crypt(private_key.encode())

    if file is not None:
        data = open_file(file)

    if data is None:
        raise ValueError('you must specify either --file or --data')

    decrypted = crypt.decrypt(NEW_LINE_EXPR.sub('', data).encode())
    click.echo(decrypted)


def _echo_config(section: str, config: Mapping):
    click.echo(f'[{section}]')
    click.echo(f"private_key: {config[section]['private_key']}")
    click.echo(f"public_key: {config[section]['public_key']}")
    click.echo('----------------')


@mash.command()
@click.option('--profile', default=None)
@click.pass_obj
def getconfig(config_manager: ConfigManager, profile: str):
    config = config_manager.read()
    if profile:
        _echo_config(profile, config)
    else:
        for section in config.sections():
            _echo_config(section, config)


if __name__ == '__main__':
    mash()
