from collections import Counter

import numpy as np
from click.testing import CliRunner
from scipy.stats import entropy

from monstermash.__main__ import main

ACCEPTABLE_ENTROPY = 3.7


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
    results = runner.invoke(main, ['generate'])
    data = results.stdout.split('\n')
    assert data[1] == 'Private Key (keep is secret, keep it safe)'
    assert data[3] == 'Public Key (you can share this one)'
    assert get_entropy(data[2]) >= ACCEPTABLE_ENTROPY
    assert get_entropy(data[4]) >= ACCEPTABLE_ENTROPY
