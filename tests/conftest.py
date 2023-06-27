from click.testing import CliRunner
from pytest import fixture

from monstermash.crypt import KeyPair


@fixture(scope='session')
def keypair_one() -> KeyPair:
    return KeyPair(
        private_key='953213b36313280d35eb60875f6666c59481895894801298978d0d41671130d8',
        public_key='c1c9855e4f410284c7bcbd80532774a4b4c006f0f61423e83bb784630f4bb130',
    )


@fixture(scope='session')
def keypair_two() -> KeyPair:
    return KeyPair(
        private_key='4bb4a815c5823b7b3c0b292d3f5ab869291c692600e6aeb61d29b0779f9f5b55',
        public_key='f9fa20980d0225390474ae67e8d5bcf9389ec7886a83467944561b737bce1427',
    )


@fixture(scope='session')
def lyrics() -> str:
    with open('tests/monstermash-lyrics.txt') as f:
        content = f.read()
    return content
