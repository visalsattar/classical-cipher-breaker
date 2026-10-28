import pytest

from caesar import encrypt
from cracker import chi_squared, crack

PARAGRAPH = (
    "Security teams rarely fail because the mathematics is weak. They fail because "
    "someone reuses a password, leaves a test server open to the internet, or trusts "
    "a message that looks official. Good defenders study how attackers think, practise "
    "on systems they own, and write down what they learn so others avoid the same mistakes."
)


@pytest.mark.parametrize("key", range(26))
def test_crack_recovers_every_key(key):
    result = crack(encrypt(PARAGRAPH, key))
    assert result.key == key
    assert result.plaintext == PARAGRAPH
    assert result.confident


def test_short_text_is_not_confident():
    assert crack(encrypt("hi", 3)).confident is False


def test_english_scores_lower_than_ciphertext():
    assert chi_squared(PARAGRAPH) < chi_squared(encrypt(PARAGRAPH, 7))


def test_no_letters_scores_infinity():
    assert chi_squared("123 !?") == float("inf")
