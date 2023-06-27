import re
from collections import Counter

import numpy as np
from click.testing import CliRunner
from hypothesis import given
from hypothesis import strategies as st
from scipy.stats import entropy

from monstermash.__main__ import mash
from monstermash.crypt import KeyPair
from monstermash.utils.file import NEW_LINE_EXPR

ACCEPTABLE_ENTROPY = 3.6


def replace_new_line(text: str) -> str:
    return NEW_LINE_EXPR.sub('', text)


def get_entropy(data):
    """
    Calculate the entropy of a byte string using scipy's entropy function.

    This function first creates a byte frequency distribution,
    then uses scipy's entropy function to calculate the entropy.

    Parameters:
    data (bytes): The data to calculate the entropy of.

    Returns:
    float: The entropy of the data.
    """
    if not data:
        return 0
    # Create a byte frequency distribution
    counter = Counter(data)
    # Create a numpy array with the counts
    counts = np.array(list(counter.values()))
    # Calculate the probabilities
    probabilities = counts / len(data)
    # Use scipy's entropy function to calculate the entropy
    return entropy(probabilities, base=2)


def test_generate():
    runner = CliRunner()
    results = runner.invoke(mash, ['generate'])
    data = results.stdout.split('\n')
    assert data[1] == 'Private Key (keep is secret, keep it safe)'
    assert data[3] == 'Public Key (you can share this one)'
    assert get_entropy(data[2]) >= ACCEPTABLE_ENTROPY
    assert get_entropy(data[4]) >= ACCEPTABLE_ENTROPY


@given(st.text())
def test_encrypt_and_decrypt_priv_pub_data(keypair_one: KeyPair, keypair_two: KeyPair, text: str):
    runner = CliRunner()
    encrypted = runner.invoke(
        mash,
        [
            'encrypt',
            f'--private-key={keypair_one.private_key.get_secret_value()}',
            f'--public-key={keypair_two.public_key}',
            f'--data={text}',
        ],
    )
    assert get_entropy(encrypted.output) >= ACCEPTABLE_ENTROPY

    encrypted_text_cleaned = replace_new_line(encrypted.output)
    decrypted = runner.invoke(
        mash,
        [
            'decrypt',
            f'--private-key={keypair_two.private_key.get_secret_value()}',
            f'--data={encrypted_text_cleaned}',
        ],
    )
    assert replace_new_line(decrypted.output) == replace_new_line(text)


def test_encrypt_and_decrypt_priv_pub_file(keypair_one: KeyPair, keypair_two: KeyPair, lyrics: str):
    runner = CliRunner()

    encrypted = runner.invoke(
        mash,
        [
            'encrypt',
            f'--private-key={keypair_one.private_key.get_secret_value()}',
            f'--public-key={keypair_two.public_key}',
            f'--file=tests/monstermash-lyrics.txt',
        ],
    )
    assert get_entropy(encrypted.output) >= ACCEPTABLE_ENTROPY
    assert encrypted.output != lyrics

    encrypted_text_cleaned = replace_new_line(encrypted.output)
    decrypted = runner.invoke(
        mash,
        [
            'decrypt',
            f'--private-key={keypair_two.private_key.get_secret_value()}',
            f'--data={encrypted_text_cleaned}',
        ],
    )
    assert replace_new_line(decrypted.output) == replace_new_line(lyrics)
